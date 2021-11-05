from psychopy import visual, core, monitors
import psychopy
psychopy.prefs.hardware['audioLib'] = ['PTB', 'pyo', 'pygame', 'sounddevice']
from psychopy.sound import Sound
import pandas as pd
from port_open_send import sendTrigger

'''Set Task set'''
task_set = "MEG2p2014"


# TODO: add if already in data folder, throw error


'''Trigger list

160: probe audio start
161: test audio start
165: question screen appeared
166: user provided a response

'''

'''Set DEFAULTS'''
default_ITI = 1.5 # in seconds
task_set_path = './task_sets/' + task_set
task_set_csv_dir = task_set_path + "/csv"
task_audio_dir = task_set_path + "/audio"
experiment_start = core.getTime()
screen = 0 # which screen/monitor to use
win = None # will store window object
'''Track EVENTS: i.e., all data stored here'''
all_events = []

choice_mapping = {
    '1': {'name':'Not clearly at all','order':0},
    '2': {'name':'Slightly clearly','order':1},
    '3': {'name': 'Somewhat clearly', 'order': 2},
    '4': {'name': 'Very clearly', 'order': 3}

}

def run_block(block_num, show_instrctions_on_1 = True):

    all_events = [] #reset events

    experiment_start = core.getTime() #reset timer to the beginning of the block
    all_events.append(
        {'what': "block {} start".format(block_num), 'when': core.getTime() - experiment_start, 'content': None, 'response': None})

    csv = load_block_csv(block_num).to_dict('records')

    if block_num == 1 and show_instrctions_on_1:
        show_message("Hello and welcome to the study.\nPress any key on your keyboard to continue.")

    show_message("In every trial you will listen to two melodies in a row:\"Melody 1\", followed by \"Melody 2\".\n"
                 "The two melodies are very similar but never identical. \n"
                 "Your task is to indicate how clearly you heard the difference between the two melodies.\n" +
                 "Press any key on your keyboard to continue.")

    show_message("Please pay attention to the cross at the center of the screen throughout the task.\n" +
                 "Press any key on your keyboard to continue.")

    show_message("Experimental Block {}\n Press any key to continue.".format(block_num))

    # loop through trial information in block
    for row in csv:

        choice_trial(row, len(csv))
        save_event_data('trial_data_block_{}.json'.format(block_num)) # save after every response

    # save_event_data('trial_data_block_{}.json'.format(block_num)) #save at the end of each block
    all_events.append(
        {'what': "block {} end".format(block_num), 'when': core.getTime() - experiment_start, 'content': None,
         'response': None})
    end_experiment()


def open_window(size=None):
    all_events.append({'what':"window open",'when':core.getTime()-experiment_start,'content':None,'response':None})
    if(size): return visual.Window(size,color=[-1],screen=screen)
    return visual.Window(fullscr=True,color=[-1],screen=screen)


def show_message(msg="",keys=None,context="",store=True):
    all_events.append(
        {'what': "message displayed", 'when': core.getTime() - experiment_start, 'content': msg, 'response': None})
    msg = visual.TextStim(win, text=msg)
    msg.draw()
    win.flip()

    # escape code
    all_keys = psychopy.event.getKeys()
    if (all_keys!=None):
        if 'b' in all_keys and 'p' in all_keys:
            core.quit()

    key = psychopy.event.waitKeys(keyList=keys)

    if(store):all_events.append({'what': "keypress", 'when': core.getTime() - experiment_start, 'content': None, 'response': key,
                                 'context': context})
    return key


def choice_screen(keys=None,trigger_port=None):
    all_events.append(
        {'what': "choice_screen", 'when': core.getTime() - experiment_start, 'content': "", 'response': None})
    msg = "How clearly did you hear the difference between the two melodies?"
    option1 = "[1] Not clearly at all"
    option2 = "[2] Slightly clearly"
    option3 = "[3] Somewhat clearly"
    option4 = "[4] Very clearly"

    msg = visual.TextStim(win, text=msg)
    option1 = visual.TextStim(win, text=option1)
    option1.pos = (-0.5, -0.5)
    option2 = visual.TextStim(win, text=option2)
    option2.pos = (-0.25, -0.5)
    option3 = visual.TextStim(win, text=option3)
    option3.pos = (0.25, -0.5)
    option4 = visual.TextStim(win, text=option4)
    option4.pos = (0.5, -0.5)
    msg.draw()
    option1.draw()
    option2.draw()
    option3.draw()
    option4.draw()
    win.flip()

    if(trigger_port):
        sendTrigger(trigger_port, duration=0.01)

    # escape code
    all_keys = psychopy.event.getKeys()
    if (all_keys!=None):
        if 'b' in all_keys and 'p' in all_keys:
            core.quit()

    key = psychopy.event.waitKeys(keyList=keys)
    return key


def timed_message(msg="",time=1):
    all_events.append(
        {'what': "timed message", 'when': core.getTime() - experiment_start, 'content': msg, 'response': None})
    msg = visual.TextStim(win, text=msg)
    msg.draw()
    win.flip()
    core.wait(time)


def show_ITI(time=default_ITI,msg=""):
    all_events.append(
        {'what': "ITI", 'when': core.getTime() - experiment_start, 'content': time, 'response': None})
    ITI = visual.TextStim(win, text=msg)
    ITI.draw()
    win.flip()
    core.wait(time)


def play_file(path,msg,trigger_port,trigger_twice=False):
    all_events.append(
        {'what': "audio played", 'when': core.getTime() - experiment_start, 'content': path, 'message':msg, 'response': None})
    mySound = Sound(path)
    if (trigger_port):
        sendTrigger(trigger_port, duration=0.01)
    #if (trigger_port and trigger_twice):
    #    sendTrigger(trigger_port, duration=0.01)
    mySound.play()
    core.wait(mySound.getDuration())
    msg = visual.TextStim(win, text=msg)
    msg.draw()
    win.flip()


def start_experiment(size=None):
    '''Experiement Start'''
    all_events.append(
        {'what': "experiement start", 'when': core.getTime() - experiment_start, 'content': None, 'response': None})
    if(size): return open_window(size)
    return open_window()


def choice_trial(entry, num_of_Qs = 25):

    show_message("Block {}, Question {} of {}\nPress any key to start the trial.".format(entry['block_num'],entry['num_in_block'],num_of_Qs))
    show_ITI()
    play_file("{}/{}".format(task_audio_dir,entry['probe_file']),"",trigger_port=f'ch160',trigger_twice=False)
    show_ITI(time=0.75,msg="")
    play_file("{}/{}".format(task_audio_dir, entry['test_file']), "", trigger_port=f'ch161', trigger_twice=False)
    show_ITI(time=0.75, msg="")
    choice = choice_screen(choice_mapping.keys(),trigger_port=f'ch165')
    sendTrigger(f'ch166') #trigger when subject responsed
    choice = choice[0]
    all_events.append(
        {
            'what': "choice_response",
            'when': core.getTime() - experiment_start,
            'char': choice,
            'choice': choice_mapping[choice]['name'],
            'Q_in_Block': entry['num_in_block'],
            'Q_in_task': entry['num_in_task'],
            'probe_pitches': entry['probe'],
            'shifted_pitches': entry['shifted'],
            'shift_amount': entry['shift_amount'],
            'shift_position': entry['shift_position'],
            'set': entry['set'],
            'mode': entry['mode'],
            'mode_num': entry['mode_num'],
            'transposition': entry['transposition'],
            'probe_file': entry['probe_file'],
            'test_file': entry['test_file'],
            'block_num':entry['block_num']

        })


def end_experiment():
    all_events.append({'what': "experiement end", 'when': core.getTime() - experiment_start, 'content': None, 'response': None})
    win.close()


def load_block_csv(block_num):
    csv = pd.read_csv("{}/block_{}.csv".format(task_set_csv_dir,block_num))
    all_events.append(
        {'what': "block {} csv loaded".format(block_num), 'when': core.getTime() - experiment_start, 'content': None,
         'response': None})
    return csv


def save_event_data(filename):
    data = pd.DataFrame(all_events)
    data['time_since_last_event'] =  data['when'] - data['when'].shift(1)
    data.to_json(task_set_csv_dir + "/" + filename,orient='records')

win = start_experiment() # [800, 800]

run_block(10) #uncomment to run the block
