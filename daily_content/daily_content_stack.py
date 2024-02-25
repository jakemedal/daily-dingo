import pathlib

import aws_cdk
from aws_cdk import (
    Stack,
    aws_lambda_python_alpha as lambda_python_alpha,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_events as events,
    aws_events_targets as event_targets
)
from constructs import Construct


class DailyContentStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        role = self.create_role()
        lambda_fn = self.create_lambda(role)
        self.create_trigger(lambda_fn)

    def create_lambda(self, role):
        lambda_function = lambda_python_alpha.PythonFunction(
            self,
            "LambdaFunction",
            runtime=lambda_.Runtime.PYTHON_3_9,
            entry=str(pathlib.Path(__file__).parent.joinpath("runtime").resolve()),
            index="lambda_function.py",
            role=role,
            handler="lambda_handler",
            environment={
                'RECIPIENTS': "jake.medal@gmail.com,crystal.herrington22@gmail.com"
            },
            timeout=aws_cdk.Duration.seconds(30)
        )

        return lambda_function

    def create_role(self):
        lambda_role = iam.Role(self, id='LambdaRole',
                               assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
                               role_name='DailyContentLambdaRole',
                               managed_policies=[
                                   iam.ManagedPolicy.from_aws_managed_policy_name(
                                       'service-role/AWSLambdaBasicExecutionRole')
                               ])

        lambda_role.attach_inline_policy(iam.Policy(self, "SesPolicy", statements=[
            iam.PolicyStatement(actions=["ses:SendEmail"], resources=["*"])
        ]))

        return lambda_role

    def create_trigger(self, lambda_function):
        event_rule = events.Rule(self, "EventRule", schedule=events.Schedule.cron(hour="8", minute="15"))
        event_rule.add_target(event_targets.LambdaFunction(lambda_function))

