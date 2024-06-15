import json
import boto3
import uuid
from datetime import datetime
from decimal import Decimal
from botocore.exceptions import ClientError

# name of dynamo db table
TableName = "Tabelname"

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table(TableName)


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    # httpmethod control flow
    try:
        if "httpMethod" in event:
            if event["httpMethod"] == "OPTIONS":
                return build_response(200, "CORS preflight response", cors=True)
            elif event["httpMethod"] == "GET":
                return get_all_items()
            elif event["httpMethod"] == "POST":
                return post_note(event)
            elif event["httpMethod"] == "DELETE":
                return delete_note(event)
            elif event["httpMethod"] == "PUT":
                return edit_note(event)
            else:
                return build_response(
                    405, f'HTTP method {event["httpMethod"]} not supported', cors=True
                )
        else:
            return build_response(400, "Bad request: Missing httpMethod", cors=True)
    except Exception as e:
        print(f"Error processing request: {e}")
        return build_response(500, f"Internal server error: {e}", cors=True)


# PUT Method
def edit_note(event):
    try:
        body = json.loads(event["body"])
        note_id = body.get("id")
        if not note_id:
            return build_response(400, "Bad request: Missing note ID", cors=True)

        update_expression = "SET "
        expression_attribute_values = {}
        for key, value in body.items():
            if key != "id":
                update_expression += f"{key} = :{key}, "
                expression_attribute_values[f":{key}"] = value

        update_expression = update_expression.rstrip(", ")

        table.update_item(
            Key={"id": note_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="UPDATED_NEW",
        )

        return build_response(200, "Note updated successfully!", cors=True)
    except ClientError as e:
        print(f"Error updating note: {e}")
        return build_response(500, f"Internal server error: {e}", cors=True)
    except KeyError as e:
        print(f"KeyError: {e}")
        return build_response(400, f"Bad request: Missing parameter {e}", cors=True)


# DELETE method
def delete_note(event):
    try:
        note_id = (
            event["queryStringParameters"].get("id")
            if event.get("queryStringParameters")
            else None
        )

        if not note_id:
            return build_response(400, "Bad request: Missing note ID", cors=True)

        table.delete_item(Key={"id": note_id})
        return build_response(200, "Note deleted successfully!", cors=True)
    except ClientError as e:
        print(f"Error deleting note: {e}")
        return build_response(500, f"Internal server error: {e}", cors=True)
    except KeyError as e:
        print(f"KeyError: {e}")
        return build_response(400, f"Bad request: Missing parameter {e}", cors=True)


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

    return build_response(200, "Note created successfully!", cors=True)


# GET method
def get_all_items():
    try:
        scan_params = {"TableName": table.name}
        return build_response(200, scan_dynamo_records(scan_params, []), cors=True)
    except ClientError as e:
        print("Error:", e)
        return build_response(400, e.response["Error"]["Message"], cors=True)


# Scan the whole table items and return them
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
            if obj % 1 == 0:
                return int(obj)
            else:
                return float(obj)
        return super(DecimalEncoder, self).default(obj)


# the return response
def build_response(status_code, body, cors=False):
    headers = {"Content-Type": "application/json"}
    if cors:
        headers["Access-Control-Allow-Origin"] = "*"
        headers["Access-Control-Allow-Headers"] = "Content-Type"
        headers["Access-Control-Allow-Methods"] = "OPTIONS,POST,GET,DELETE,PUT"

    return {
        "statusCode": status_code,
        "headers": headers,
        "body": json.dumps(body, cls=DecimalEncoder),
    }
