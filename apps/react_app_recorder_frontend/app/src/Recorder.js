import React, { useState, useRef, useEffect } from "react";
import AWS from "aws-sdk";
import async from "async";
import 'bootstrap/dist/css/bootstrap.min.css';
import { Modal, Button } from 'react-bootstrap';
import './style.css';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const useQuery = () => {
  return new URLSearchParams(window.location.search);
};

let micStatus = false;

const AudioRecorder = () => {
  const [isRecording, setIsRecording] = useState(false);  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDoneModalOpen, setIsDoneModalOpen] = useState(false);
  const [isAnyRecording, setIsAnyRecording] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const intervalRef = useRef(null);
  const [timer, setTimer] = useState(0);
  const [devices, setDevices] = useState([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState("");

  const query = useQuery();
  const patient_id = query.get("patient_id");
  const encounter_id = query.get("encounter_id");
  let assessment_id = query.get("assessment_id");
  let assessment_type = query.get("assessment_type");
  if (!assessment_id) assessment_id = "";
  if (!assessment_type) assessment_type = "";
  const raw_folder_path = "raw/" + patient_id + "/" + encounter_id + "/";

  // Configure AWS SDK
  AWS.config.update({
    region: "us-east-1"
  });

  const s3 = new AWS.S3();

  // Initialize async queue
  const uploadQueue = async.queue((audioBlob, callback) => {
    const filename = raw_folder_path + "audio_" + Date.now().toString() + ".webm";
    const params = {
      Bucket: "dev-acutedge-recordings",
      Key: filename,
      Body: audioBlob,
      ContentType: "audio/webm",
      ACL: "private",
    };

    console.log("Uploading to S3:", filename);
    s3.upload(params, (err, data) => {
      if (err) {
        console.error("S3 upload error:", err);
        callback(err);
      } else {
        console.log("Successfully uploaded to S3:", data);
        callback(null, data);
      }
    });
  }, 2);

  const stopRecordingForcefully = (mediaRecorderRef, intervalRef, stream) => {
    console.warn("Forcing stop of recording due to an error.");
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop();
    }
    setIsRecording(false);
    toast.error("Something went wrong while recording, please start again.");
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
    }
    clearInterval(intervalRef.current);
    setTimer(0);
  };

  const startRecording = async () => {
    console.log("Attempting to start recording...");
    try {
      let permission;
      try {
        permission = await navigator.permissions.query({ name: "microphone" });
      } catch (permErr) {
        console.log("Permission query not supported:", permErr);
      }

      if (!permission || permission.state === "granted") {
        micStatus = true;
        setTimer(0);
        setIsRecording(true);
        toast.info("Recording started");

        const constraints = selectedDeviceId
          ? { audio: { deviceId: { exact: selectedDeviceId } } }
          : { audio: true };

        console.log("Using constraints:", constraints);
        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        console.log("Got stream:", stream);

        mediaRecorderRef.current = new MediaRecorder(stream, { mimeType: "audio/webm" });
        audioChunksRef.current = [];

        mediaRecorderRef.current.ondataavailable = (event) => {
          console.log("Data available:", event.data.size, "bytes");
          audioChunksRef.current.push(event.data);
          setIsAnyRecording(true);
        };

        mediaRecorderRef.current.onstop = async () => {
          console.log("Recorder stopped, processing data...");
          const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
          console.log("Final blob size:", audioBlob.size, "bytes");
          if (audioBlob.size === 0) {
            console.warn("Recorded blob is empty. No audio captured.");
          }

          uploadQueue.push(audioBlob, (err) => {
            if (err) {
              console.error("Failed to process audio chunk:", err);
              stopRecordingForcefully(mediaRecorderRef, intervalRef, stream);
            }
          });
          audioChunksRef.current = [];

          if (!micStatus) {
            console.log("Mic status off, stopping tracks...");
            stream.getTracks().forEach(track => track.stop());
          }
        };

        mediaRecorderRef.current.start();
        console.log("MediaRecorder started with state:", mediaRecorderRef.current.state);

        intervalRef.current = setInterval(() => {
          if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
            console.log("Splitting recording chunk...");
            mediaRecorderRef.current.stop();
            mediaRecorderRef.current.start();
          }
        }, 1800000); // 30 minutes

        if (permission) {
          permission.onchange = (event) => {
            console.log("Microphone permission changed:", event.target.state);
            if (event.target.state === 'denied') {
              stopRecordingForcefully(mediaRecorderRef, intervalRef, stream);
            }
          };
        }

      } else {
        console.error("Microphone permission not granted.");
        toast.error("Turn on microphone permission.");
      }
    } catch (error) {
      console.error("Error starting recording:", error);
      toast.error("Failed to start recording. Check console for details.");
    }
  };

  const stopRecording = () => {
    console.log("Stopping recording...");
    setIsRecording(false);
    clearInterval(intervalRef.current);
    setTimer(0);
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop();
    }
    micStatus = false;
    toast.success("Recording stopped and saved successfully");
  };

  const deleteAllRecordings = () => {
    console.log("Deleting all recordings...");
    const params = {
      Bucket: "dev-acutedge-recordings",
      Prefix: raw_folder_path,
    };

    s3.listObjectsV2(params, (err, data) => {
      if (!err) {
        const deleteParams = {
          Bucket: "dev-acutedge-recordings",
          Delete: { Objects: [] },
        };
        
        data.Contents.forEach((item) => {
          deleteParams.Delete.Objects.push({ Key: item.Key });
        });

        if (deleteParams.Delete.Objects.length > 0) {
          s3.deleteObjects(deleteParams, (err, data) => {
            if (!err) {
              setIsAnyRecording(false);
              toast.success("Recording deleted successfully");
              console.log("All recordings deleted.");
            } else {
              console.error("Error deleting objects:", err);
            }
          });
        } else {
          toast.warning("No recording found to delete");
          console.warn("No objects to delete.");
        }
      } else {
        console.error("Error listing objects:", err);
      }
    });
  };

  const deleteModalOpen = () => {
    setIsModalOpen(true);
  };

  const handleModalClose = () => {
    setIsModalOpen(false);
  };

  const handleDeleteConfirm = () => {
    deleteAllRecordings();
    setIsModalOpen(false);
  };

  const submitConversationAPI = async () => {
    console.log("Submitting conversation...");
    try {
      setIsCompleted(true);
      const response = await fetch("https://f8txi4kkj2.execute-api.us-east-1.amazonaws.com/v1/recording/submit", {
        method: "POST",
        body: JSON.stringify({
          patient_id: patient_id,
          encounter_id: encounter_id,
          assessment_id: assessment_id,
          assessment_type: assessment_type
        }),
      });
      console.log("Submit response:", response);
    } catch (error) {
      setIsCompleted(false);
      console.error("Error submitting recordings:", error);
    }
  };

  const doneModalOpen = () => {
    setIsDoneModalOpen(true);
  };

  const handleDoneModalClose = () => {
    setIsDoneModalOpen(false);
  };

  const handleDoneConfirm = () => {
    submitConversationAPI();
    setIsDoneModalOpen(false);
  };

  const secondToHHMMSS = (d) => {
    d = Number(d);
    const h = Math.floor(d / 3600);
    const m = Math.floor((d % 3600) / 60);
    const s = Math.floor((d % 3600) % 60);
  
    const hh = h < 10 ? '0' + h : '' + h;
    const mm = m < 10 ? '0' + m : '' + m;
    const ss = s < 10 ? '0' + s : '' + s;
  
    return `${hh}:${mm}:${ss}`;
  };

  useEffect(() => {
    navigator.mediaDevices.enumerateDevices()
      .then((deviceInfos) => {
        const audioInputs = deviceInfos.filter(device => device.kind === "audioinput");
        console.log("Audio input devices found:", audioInputs);
        setDevices(audioInputs);
        if (audioInputs.length > 0) {
          setSelectedDeviceId(audioInputs[0].deviceId);
        }
      })
      .catch(err => console.error("Error enumerating devices:", err));
  }, []);

  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      if (
        mediaRecorderRef.current &&
        mediaRecorderRef.current.state !== "inactive"
      ) {
        mediaRecorderRef.current.stop();
      }
    };
  }, []);
  
  useEffect(() => {
    const timerTask = setTimeout(() => {
      if (isRecording) {
        setTimer(prev => prev + 1);
      }
    }, 1000);
    return () => clearTimeout(timerTask);
  }, [timer, isRecording]);

  return (
    <>
<div className="page-content"> 
  <ToastContainer />
  <div className="main-wrapper" style={{ paddingBottom: "20px" }}>
    {devices.length > 0 && (
      <div 
        className="title-and-dropdown" 
        style={{
          display: "flex", 
          alignItems: "center", 
          justifyContent: "space-between", 
          marginBottom: "15px"
        }}
      >
        <h1 style={{ margin: 0 }}>Audio Recorder</h1>
        <select
          id="micSelect"
          className="form-control mic-dropdown"
          value={selectedDeviceId}
          onChange={(e) => setSelectedDeviceId(e.target.value)}
          style={{ maxWidth: "300px", borderRadius: "4px" }}
        >
          {devices.map((device) => (
            <option key={device.deviceId} value={device.deviceId}>
              {device.label || `Microphone ${device.deviceId}`}
            </option>
          ))}
        </select>
      </div>
    )}
    <div className="recording-block">
      <div className="buttons-grp">
        {isRecording ? (
          <button className="btn pause-btn" onClick={stopRecording}>Stop</button>
        ) : (
          <>
            <button className={`btn start-btn ${isCompleted ? 'disabled' : ''}`} onClick={startRecording}>Start</button>
            <button className={`btn complete-btn btn-info ${(!isAnyRecording || isCompleted) ? 'disabled' : ''}`} onClick={doneModalOpen}>Done</button>
            <button className="btn pause-btn" onClick={deleteModalOpen}>Delete</button>
          </>
        )}
      </div>
      <div className="wave-wrapper">
        <div className="recording-view">
          <button className={isRecording ? "Rec rec-btn" : "rec-btn gray-rec-btn"}>Recording</button>
          <span className={isRecording ? "" : "gray-rec-btn-text"}> Recording</span>
        </div>
        {isRecording && 
          <div style={{display: "flex", alignItems: "center", gap: "20px"}}>
            <div className="boxContainer">
              <div className="box box1"></div>
              <div className="box box2"></div>
              <div className="box box3"></div>
              <div className="box box4"></div>
              <div className="box box5"></div>
            </div>
          </div>
        }
        {isRecording && 
          <div className="timer">
            <span>{secondToHHMMSS(timer)}</span>
          </div>
        }
      </div>
    </div>
  </div>
</div>

      <Modal show={isModalOpen} onHide={handleModalClose}>
        <Modal.Header closeButton>
          <Modal.Title>Confirm Delete</Modal.Title>
        </Modal.Header>
        <Modal.Body>Are you sure you want to delete recording?</Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleModalClose}>
            Close
          </Button>
          <Button variant="danger" onClick={handleDeleteConfirm}>
            Yes, Delete
          </Button>
        </Modal.Footer>
      </Modal>
      <Modal show={isDoneModalOpen} onHide={handleDoneModalClose}>
        <Modal.Header closeButton>
          <Modal.Title>Confirm Submit</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>Are you sure you want to submit the recording?</p>
          <small className="text-danger">Please ensure the conversation has ended before submitting. Once submitted, the recording cannot be reversed or modified.</small>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleDoneModalClose}>
            Close
          </Button>
          <Button variant="danger" onClick={handleDoneConfirm}>
            Submit
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
};

export default AudioRecorder;
