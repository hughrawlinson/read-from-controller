import serial
import mido
import atexit

midiport = mido.open_output()

def exit_handler():
    midiport.close()
    print("Bye!")

noteMap = [
    [45,44,43,42,41,40],
    [50,49,48,47,46,45],
    [55,54,53,52,51,50],
    [60,59,58,57,56,55],
    ]

frets = [91, 128, 181, 250, 328, 415]

noteState = [(),(),(),()]

DEBOUNCING = "DEBOUNCING"
NOTE_ON = "NOTE_ON"

def playNoteOn(note):
    midiport.send(mido.Message('note_on', note=note))
    print("Note On:", note)

def playNoteOff(note):
    midiport.send(mido.Message('note_off', note=note, velocity=0))
    print("Note Off:", note)

def handleNoteOn(string, fret):
    try:
        (savedFret, state) = noteState[string]
        if state is DEBOUNCING:
            noteState[string] = (fret, NOTE_ON)
            playNoteOn(noteMap[string][fret])
        elif state is NOTE_ON:
            if savedFret is not fret:
                noteState[string] = (fret, NOTE_ON)
                playNoteOff(noteMap[string][savedFret])
                playNoteOn(noteMap[string][fret])
    except ValueError:
        noteState[string] = (fret, DEBOUNCING)

def handleNoteOff(string):
    try:
        (savedFret, state) = noteState[string]
        noteState[string] = ()
        playNoteOff(noteMap[string][savedFret])
    except Exception:
        pass

if __name__ == "__main__":
    with serial.Serial('/dev/ttyACM0', 115200, timeout=1) as ser:
        while True:
            value = ser.readline().strip()
            [bytestring, byteresistance] = value.split(b':')
            string = int(bytestring)
            resistance = int(byteresistance)
            if resistance < 1000:
                for index, fretVal in enumerate(frets):
                    if -10 <= fretVal - resistance <= 10:
                        handleNoteOn(string, index)
            else:
                handleNoteOff(string)
