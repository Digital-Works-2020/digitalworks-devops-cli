"""
AWSClient: OOP client for AWS SSO cost operations.
Follows PEP8 and Codacy standards.
"""

import boto3
import botocore
from datetime import datetime, timedelta
from typing import Optional, Dict
import subprocess
import os

class AWSClient:
    """OOP client for AWS SSO cost operations."""
    def __init__(self, profile: str) -> None:
        self.profile = profile
        self.session = boto3.Session(profile_name=profile)
        self.ce = self.session.client('ce')

    @staticmethod
    def list_profiles() -> list:
        """List available AWS CLI profiles."""
        import configparser
        profiles = []
        aws_config = os.path.expanduser('~/.aws/config')
        aws_creds = os.path.expanduser('~/.aws/credentials')
        parser = configparser.ConfigParser()
        if os.path.exists(aws_config):
            parser.read(aws_config)
            for section in parser.sections():
                if section.startswith('profile '):
                    profiles.append(section.replace('profile ', ''))
        if os.path.exists(aws_creds):
            parser.read(aws_creds)
            for section in parser.sections():
                if section not in profiles:
                    profiles.append(section)
        return sorted(set(profiles))

    def check_credentials(self) -> bool:
        """Check if the current profile's credentials are valid and not expired."""
        try:
            sts = self.session.client('sts')
            sts.get_caller_identity()
            return True
        except botocore.exceptions.ClientError as exc:
            if 'ExpiredToken' in str(exc):
                return False
            raise
        except Exception:
            return False

    @staticmethod
    def sso_login(profile: str) -> None:
        """Prompt user to run aws sso login for the given profile."""
        print(f"AWS credentials for profile '{profile}' are expired or missing.")
        print(f"Please run: aws sso login --profile {profile}")
        subprocess.run(["aws", "sso", "login", "--profile", profile], check=True)

    def get_month_cost(self, year: int, month: int) -> Optional[float]:
        """Get AWS cost for a given year and month."""
        start = datetime(year, month, 1)
        if month == 12:
            end = datetime(year + 1, 1, 1)
        else:
            end = datetime(year, month + 1, 1)
        try:
            resp = self.ce.get_cost_and_usage(
                TimePeriod={
                    'Start': start.strftime('%Y-%m-%d'),
                    'End': end.strftime('%Y-%m-%d')
                },
                Granularity='MONTHLY',
                Metrics=['UnblendedCost']
            )
            amount = resp['ResultsByTime'][0]['Total']['UnblendedCost']['Amount']
            return float(amount)
        except Exception as exc:
            print(f"Error fetching AWS cost: {exc}")
            return None
