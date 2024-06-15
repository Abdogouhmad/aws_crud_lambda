# NoteDB Lambda Function

This project provides an AWS Lambda function for a note-taking application that uses Amazon DynamoDB as its backend. The Lambda function supports CRUD operations (Create, Read, Update, Delete) and handles CORS preflight requests.

## Table of Contents

- [NoteDB Lambda Function](#notedb-lambda-function)
  - [Table of Contents](#table-of-contents)
  - [Architecture](#architecture)
  - [Endpoints](#endpoints)
  - [Request and Response Formats](#request-and-response-formats)
    - [GET /notes](#get-notes)
    - [DELETE /notes?id={note_id}](#delete-notesidnote_id)
    - [PUT /notes](#put-notes)
  - [Dependencies](#dependencies)
  - [Error Handling](#error-handling)
  - [Related repo](#related-repo)

## Architecture

The Lambda function interacts with a DynamoDB table named `notedb` to store and manage notes. Each note consists of the following attributes:

- `id` (string): A unique identifier for the note.
- `CreationTime` (number): The timestamp when the note was created.
- `Title` (string): The title of the note.
- `Description` (string): A description of the note.
- `NoteType` (string): The type of the note.
- `Note` (string): The content of the note.
- `Username` (string): The username of the note's creator.

## Endpoints

The Lambda function supports the following HTTP methods:

- `OPTIONS`: Handles CORS preflight requests.
- `GET`: Retrieves all notes.
- `POST`: Creates a new note.
- `DELETE`: Deletes a note by ID.
- `PUT`: Updates an existing note by ID.

## Request and Response Formats

### GET /notes

Retrieves all notes.

**Response:**

````json
{
  "notes": [
    {
      "id": "string",
      "CreationTime": "number",
      "Title": "string",
      "Description": "string",
      "NoteType": "string",
      "Note": "string",
      "Username": "string"
    },
    ...
  ]
}

### POST /notes

Creates a new note.

**Request:**

```json
{
  "title": "string",
  "description": "string",
  "notetype": "string",
  "note": "string",
  "username": "string"
}
````

**Response:**

```json
"Note created successfully!"
```

### DELETE /notes?id={note_id}

Deletes a note by ID.

**Response:**

"Note deleted successfully!"

### PUT /notes

Updates an existing note by ID.

**Request:**

```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "notetype": "string",
  "note": "string",
  "username": "string"
}
```

**Response:**

```json
"Note updated successfully!"
```

## Dependencies

- boto3: AWS SDK for Python to interact with DynamoDB.
- uuid: To generate unique identifiers for notes.
- datetime: To handle creation timestamps.
- decimal: For accurate handling of decimal numbers in DynamoDB.
- botocore.exceptions: To handle exceptions from the AWS SDK.

## Error Handling

The Lambda function includes error handling for:

- Missing HTTP methods.
- Invalid or missing request parameters.
- DynamoDB client errors.
- General exceptions to ensure the Lambda function does not crash and provides meaningful error messages.

## Related repo

- [NTM](https://github.com/Abdogouhmad/NTM)
