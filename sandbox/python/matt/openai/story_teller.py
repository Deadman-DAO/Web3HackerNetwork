import boto3
import pyaudio
import wave
import io
import requests
import json

# Create a client for the Amazon Transcribe service
transcribe = boto3.client('transcribe')

# Create a client for the Amazon Polly service
tts_client = boto3.client("polly")

while True:
    # Prompt the user for a story subject
    print("What kind of story would you like me to tell?")

    # Record the user's input
    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 1
    fs = 44100
    seconds = 5
    p = pyaudio.PyAudio()
    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    frames = []
    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)

    # Stop recording and save the audio file
    stream.stop_stream()
    stream.close()
    p.terminate()

    file_name = "input.wav"
    wavefile = wave.open(file_name, 'wb')
    wavefile.setnchannels(channels)
    wavefile.setsampwidth(p.get_sample_size(sample_format))
    wavefile.setframerate(fs)
    wavefile.writeframes(b''.join(frames))
    wavefile.close()

    # Transcribe the audio file
    job_name = "example-job"
    response = transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={
            "MediaFileUri": "file://" + file_name
        },
        MediaFormat=file_name.split(".")[-1],
        LanguageCode="en-US"
    )

    # Check the status of the transcription job
    status = transcribe.get_transcription_job(TranscriptionJobName=job_name)['TranscriptionJob']['TranscriptionJobStatus']

    # Wait for the transcription job to complete
    while status == 'IN_PROGRESS':
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)['TranscriptionJob']['TranscriptionJobStatus']

    # Get the transcription result
    if status == 'COMPLETED':
        transcription_url = transcribe.get_transcription_job(TranscriptionJobName=job_name)['TranscriptionJob']['Transcript']['TranscriptFileUri']
        response = requests.get(transcription_url)
        text = response.text
    else:
        print("Transcription failed with status: " + status)
        continue

    # Use GPT-3 to generate a story
    headers = {
        'Content-Type': 'application/json',
    }

    data = """
    {
      """ + text + """
    }
    """

    response = requests.post('https://api.openai.com/v1/engines/text-davinci-002/jobs', headers=headers, data=data)
    # Use Amazon Polly to generate speech from the story text
    response = tts_client.synthesize_speech(
        Engine='neural',
        VoiceId='Matthew',
        Text=response.text,
        OutputFormat='mp3'
    )

    # Save the speech audio to a file
    with open("output.mp3", "wb") as f:
        f.write(response['AudioStream'].read())

    # Play the speech audio
    wf = wave.open("output.mp3", "rb")
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    data = wf.readframes(chunk)
    while data:
        stream.write(data)
        data = wf.readframes(chunk)
    stream.stop_stream()
    stream.close()
    p.terminate()
