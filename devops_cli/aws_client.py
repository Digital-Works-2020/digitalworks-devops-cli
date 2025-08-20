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
    """OOP client for AWS SSO operations."""
    def __init__(self, profile: str) -> None:
        self.profile = profile
        self.session = boto3.Session(profile_name=profile)
        self.ce = self.session.client('ce')

    def list_instances_by_state(self) -> Dict[str, list]:
        """List EC2 instances grouped by their state (e.g., running, stopped)."""
        ec2 = self.session.client('ec2')
        try:
            paginator = ec2.get_paginator('describe_instances')
            state_map = {}
            for page in paginator.paginate():
                for reservation in page.get('Reservations', []):
                    for instance in reservation.get('Instances', []):
                        state = instance.get('State', {}).get('Name', 'unknown')
                        instance_id = instance.get('InstanceId')
                        # Try to get Name tag
                        name = None
                        for tag in instance.get('Tags', []):
                            if tag.get('Key') == 'Name':
                                name = tag.get('Value')
                                break
                        entry = {'InstanceId': instance_id}
                        if name:
                            entry['Name'] = name
                        state_map.setdefault(state, []).append(entry)
            return state_map
        except Exception as exc:
            print(f"Error listing EC2 instances: {exc}")
            return {}

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
