import aws_cdk as core
import aws_cdk.assertions as assertions

from daily_content.daily_content_stack import DailyContentStack

# example tests. To run these tests, uncomment this file along with the example
# resource in daily_content/daily_content_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = DailyContentStack(app, "daily-content")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
