from flask import *
from flask_socketio import SocketIO, emit
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app)



task_lock_staging = threading.Lock()
task_lock_qa = threading.Lock()


# button_clicked = False
@app.route('/')
def index():
    return render_template('index_socket_lock.html')


def get_task_lock(environment_input):
    if environment_input == 'Staging':
        return task_lock_staging
    elif environment_input == 'QA':
        return task_lock_qa
    else:
        return threading.Lock()

@app.route('/perform_task', methods=['POST'])
def perform_task():
    try:
        environmentInput = request.form['environmentInput']
        print("environmentInput",environmentInput)
        with get_task_lock(environmentInput):
            time.sleep(5)
            print(environmentInput,"donenn")
            return jsonify({'message': 'Task completed!'})
    except Exception as e:
        return jsonify({'error': str(e)})



@socketio.on('button_click')
def handle_button_click(data):
    environment_input = data.get('environmentInput')
    button_clicked = data.get('button_clicked')
    print(environment_input,button_clicked)
    if environment_input == 'Staging':
        with task_lock_staging:
            button_clicked_staging = button_clicked
            emit('button_clicked', {'clicked': button_clicked_staging, 'environmentInput': environment_input}, broadcast=True)
    elif environment_input == 'QA':
        with task_lock_qa:
            button_clicked_qa = button_clicked
            emit('button_clicked', {'clicked': button_clicked_qa, 'environmentInput': environment_input}, broadcast=True)

@app.route('/iframe_content', methods=['POST','GET'])
def iframe_content():
    environmentInput=request.form['environmentInput']
    return render_template('iframe_content.html', staging_jenkins=environmentInput)


    
if __name__ == '__main__':
    socketio.run(app, debug=True,host='0.0.0.0')