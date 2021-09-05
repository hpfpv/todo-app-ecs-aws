from flask import Flask, jsonify, json, Response, request
from flask_cors import CORS
import logging
import todoService


logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)
CORS(app)

@app.route('/<userID>/todos', methods=['GET'])
def getTodos(userID):
    if (request.args.get('search')):
        print(f"Getting filtered for user {userID}")
        filter = request.args.get('search')
        response = todoService.getSearchedTodos(userID, filter)
        logger.info(response)
    else:
        print(f"Getting all todos for user {userID}")
        response = todoService.getTodos(userID)
        logger.info(response)

    flaskResponse = Response(json.dumps(response))
    flaskResponse.headers["Content-Type"] = "application/json"
    flaskResponse.headers["Access-Control-Allow-Origin"] = "https://todo2.houessou.com"

    return flaskResponse

@app.route('/<userID>/todos/<todoID>', methods=['GET'])
def getTodo(userID, todoID):
    print(f'Getting todo: {todoID}')
    response = todoService.getTodo(todoID)

    flaskResponse = Response(response)
    flaskResponse.headers["Content-Type"] = "application/json"
    flaskResponse.headers["Access-Control-Allow-Origin"] = "https://todo2.houessou.com"

    return flaskResponse
    
@app.route('/<userID>/todos/<todoID>/delete', methods=['DELETE'])
def deleteTodo(userID, todoID):
    print(f"deleting todo {todoID}")
    todoService.deleteTodoFilesS3(userID, todoID)
    todoService.deleteTodoFilesDynamo(todoID)
    todoService.deleteTodo(todoID)
    
    flaskResponse = Response({})
    flaskResponse.success = True
    flaskResponse.headers["Content-Type"] = "application/json"
    flaskResponse.headers["Access-Control-Allow-Origin"] = "https://todo2.houessou.com"

    return flaskResponse

@app.route('/<userID>/todos/add', methods=['POST'])
def addTodo(userID):
    eventBody = request.json
    response = todoService.addTodo(userID, eventBody)

    flaskResponse = Response(response)
    flaskResponse.success = True
    flaskResponse.headers["Content-Type"] = "application/json"
    flaskResponse.headers["Access-Control-Allow-Origin"] = "https://todo2.houessou.com"

    return flaskResponse

@app.route('/<userID>/todos/<todoID>/complete', methods=['POST'])
def completeTodo(userID, todoID):
    response = todoService.completeTodo(todoID)

    flaskResponse = Response(response)
    flaskResponse.headers["Content-Type"] = "application/json"
    flaskResponse.headers["Access-Control-Allow-Origin"] = "https://todo2.houessou.com"

    return flaskResponse

@app.route('/<userID>/todos/<todoID>/addnotes', methods=['POST'])
def addTodoNotes(userID, todoID):

    notes = request.json["notes"]
    
    logger.info(f'adding notes for : {todoID}')
    response = todoService.addTodoNotes(todoID, notes)

    flaskResponse = Response(response)
    flaskResponse.headers["Content-Type"] = "application/json"
    flaskResponse.headers["Access-Control-Allow-Origin"] = "https://todo2.houessou.com"

    return flaskResponse

#route for health checks only.
@app.route('/', methods=['GET'])
def healthCheck():
        
    flaskResponse = Response("Nothing here. Health checks only!")
    flaskResponse.success = True
    flaskResponse.headers["Content-Type"] = "application/json"
    flaskResponse.headers["Access-Control-Allow-Origin"] = "https://todo2.houessou.com"

    return flaskResponse


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)