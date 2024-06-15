import json
import boto3
import uuid
from datetime import datetime
from decimal import Decimal
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("notedb")


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    try:
        # Check for HTTP method
        if "httpMethod" in event:
            if event["httpMethod"] == "OPTIONS":
                # Respond to CORS preflight request
                return {
                    "statusCode": 200,
                    "headers": {
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Headers": "Content-Type",
                        "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
                    },
                    "body": json.dumps("CORS preflight response"),
                }
            elif event["httpMethod"] == "GET":
                return get_all_items()
            elif event["httpMethod"] == "POST":
                return post_note(event=event)
            elif event["httpMethod"] == "DELETE":
                return delete_note(event)
            elif event["httpMethod"] == "PUT":
                return edite_note(event)
            else:
                return {
                    "statusCode": 405,
                    "headers": {
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Headers": "Content-Type",
                        "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
                    },
                    "body": json.dumps(
                        f'HTTP method {event["httpMethod"]} not supported'
                    ),
                }
        else:
            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
                },
                "body": json.dumps("Bad request: Missing httpMethod"),
            }
    except Exception as e:
        print(f"Error processing request: {e}")
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
            "body": json.dumps(f"Internal server error: {e}"),
        }


# PUT method
def edite_note(event):
    try:
        body = json.loads(event["body"])
        note_id = body.get("id")
        if not note_id:
            return build_response(400, "Bad request: Missing note ID")

        update_expression = "set "
        expression_attribute_values = {}
        for key, value in body.items():
            if key != "id":
                update_expression += f"{key} = :{key}, "
                expression_attribute_values[f":{key}"] = value

        # Remove the trailing comma and space from the update_expression
        update_expression = update_expression.rstrip(", ")

        response = table.update_item(
            Key={"id": note_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="UPDATED_NEW"
        )

        return build_response(200, "Note updated successfully!")
    except ClientError as e:
        print(f"Error updating note: {e}")
        return build_response(500, f"Internal server error: {e}")
    except KeyError as e:
        print(f"KeyError: {e}")
        return build_response(400, f"Bad request: Missing parameter {e}")


# DELETE method
def delete_note(event):
    try:
        if "queryStringParameters" in event and event["queryStringParameters"]:
            note_id = event["queryStringParameters"].get("id")
        else:
            return build_response(400, "Bad request: Missing note ID")

        if not note_id:
            return build_response(400, "Bad request: Missing note ID")

        response = table.delete_item(Key={"id": note_id})
        return build_response(200, "Note deleted successfully!")
    except ClientError as e:
        print(f"Error deleting note: {e}")
        return build_response(500, f"Internal server error: {e}")
    except KeyError as e:
        print(f"KeyError: {e}")
        return build_response(400, f"Bad request: Missing parameter {e}")


# POST method
def post_note(event):
    body = json.loads(event["body"])
    note_id = str(uuid.uuid4())
    creation_time = int(datetime.utcnow().timestamp())

    note = {
        "id": note_id,
        "CreationTime": creation_time,
        "Title": body["title"],
        "Description": body["description"],
        "NoteType": body["notetype"],
        "Note": body["note"],
        "Username": body["username"],
    }

    table.put_item(Item=note)

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        },
        "body": json.dumps("Note created successfully!"),
    }


# GET method
def get_all_items():
    try:
        scan_params = {"TableName": table.name}
        return build_response(200, scan_dynamo_records(scan_params, []))
    except ClientError as e:
        print("Error:", e)
        return build_response(400, e.response["Error"]["Message"])


# helper function for scanning records of the table
def scan_dynamo_records(scan_params, item_array):
    response = table.scan(**scan_params)
    item_array.extend(response.get("Items", []))

    if "LastEvaluatedKey" in response:
        scan_params["ExclusiveStartKey"] = response["LastEvaluatedKey"]
        return scan_dynamo_records(scan_params, item_array)
    else:
        return {"notes": item_array}


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            # Check if it's an int or a float
            if obj % 1 == 0:
                return int(obj)
            else:
                return float(obj)
        # Let the base class default method raise the TypeError
        return super(DecimalEncoder, self).default(obj)


# response builder
def build_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json",
        },
        "body": json.dumps(body, cls=DecimalEncoder),
    }
