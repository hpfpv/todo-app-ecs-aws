from flask import Flask, jsonify, json, Response, request
from flask_cors import CORS
import logging
import os
import todoFilesService


logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)
CORS(app)

#route for health checks only.
@app.route('/', methods=['GET'])
def healthCheck():
        
    response = {
        "info": "Nothing here. Health checks only!"
    }
    flaskResponse = Response(json.dumps(response))
    flaskResponse.status = "success"
    flaskResponse.status_code = 200
    flaskResponse.headers["Content-Type"] = "application/json"
    flaskResponse.headers["Access-Control-Allow-Origin"] = "'https://todo2.houessou.com','https://todo.houessou.com'"

    return flaskResponse

# route for get todo files
@app.route('/<todoID>/files', methods=['GET'])
def getTodoFiles(todoID):
    
    print(f"Getting all files for todo {todoID}")
    response = todoFilesService.getTodosFiles(todoID)

    logger.info(response)

    flaskResponse = Response(json.dumps(response))
    flaskResponse.headers["Content-Type"] = "application/json"
    flaskResponse.headers["Access-Control-Allow-Origin"] = "'https://todo2.houessou.com','https://todo.houessou.com'"

    return flaskResponse


# route for add todo files
@app.route('/<todoID>/files/upload', methods=['POST'])
def addTodoFiles(todoID):
    eventBody = request.json
    response = todoFilesService.addTodoFiles(todoID, eventBody)

    flaskResponse = Response(response)
    flaskResponse.status = "success"
    flaskResponse.status_code = 200
    flaskResponse.headers["Content-Type"] = "application/json"
    flaskResponse.headers["Access-Control-Allow-Origin"] = "'https://todo2.houessou.com','https://todo.houessou.com'"

    return flaskResponse


#route for delete todo files
@app.route('/<todoID>/files/<fileID>/delete', methods=['GET', 'DELETE'])
def deleteTodoFile(todoID, fileID):
    eventBody = request.json
    bucketCDN = os.environ['TODOFILES_BUCKET_CDN']

    filePath = eventBody["filePath"]
    fileKey = str(filePath).replace(f'https://{bucketCDN}/', '').replace('%40','@')

    print(f"deleting file {fileID}")
    todoFilesService.deleteTodosFileS3(fileKey)
    todoFilesService.deleteTodosFileDynamo(fileID)
    

    flaskResponse = Response({})
    flaskResponse.status = "success"
    flaskResponse.status_code = 200
    flaskResponse.headers["Content-Type"] = "application/json"
    flaskResponse.headers["Access-Control-Allow-Origin"] = "'https://todo2.houessou.com','https://todo.houessou.com'"

    return flaskResponse


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081, debug=True)