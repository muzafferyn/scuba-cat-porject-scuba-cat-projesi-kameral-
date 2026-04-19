import { HandLandmarker, FilesetResolver } from "@mediapipe/tasks-vision";

const video = document.getElementById("webcam");
const canvasElement = document.getElementById("output_canvas");
const canvasCtx = canvasElement.getContext("2d");
const statusText = document.getElementById("status");
const detectionDot = document.getElementById("detectionDot");
const scubaCatContainer = document.getElementById("scubaCatContainer");

let handLandmarker = undefined;
let runningMode = "VIDEO";
let lastVideoTime = -1;

const createHandLandmarker = async () => {
  const vision = await FilesetResolver.forVisionTasks(
    "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.34/wasm"
  );
  handLandmarker = await HandLandmarker.createFromOptions(vision, {
    baseOptions: {
      modelAssetPath: `https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task`,
      delegate: "GPU"
    },
    runningMode: runningMode,
    numHands: 2
  });
  statusText.innerText = "Kamera Hazır - Elini Kaldır!";
  detectionDot.classList.remove("hidden");
  startCamera();
};

createHandLandmarker();

function startCamera() {
  navigator.mediaDevices.getUserMedia({ video: true }).then((stream) => {
    video.srcObject = stream;
    video.addEventListener("loadeddata", predictWebcam);
  });
}

function createBubbles() {
  const bubblesContainer = document.querySelector('.bubbles');
  if (!bubblesContainer) return;
  
  for(let i=0; i<5; i++) {
    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    const size = Math.random() * 20 + 10;
    bubble.style.width = `${size}px`;
    bubble.style.height = `${size}px`;
    bubble.style.left = `${Math.random() * 100}%`;
    bubble.style.bottom = '0';
    bubble.style.animationDelay = `${Math.random() * 2}s`;
    bubblesContainer.appendChild(bubble);
    setTimeout(() => bubble.remove(), 3000);
  }
}

async function predictWebcam() {
  canvasElement.style.width = video.videoWidth;
  canvasElement.style.height = video.videoHeight;
  canvasElement.width = video.videoWidth;
  canvasElement.height = video.videoHeight;

  if (lastVideoTime !== video.currentTime) {
    lastVideoTime = video.currentTime;
    const results = handLandmarker.detectForVideo(video, lastVideoTime);
    
    canvasCtx.save();
    canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
    
    if (results.landmarks && results.landmarks.length > 0) {
      detectionDot.classList.add("active");
      scubaCatContainer.classList.remove("hidden");
      setTimeout(() => scubaCatContainer.classList.add("active"), 10);
      
      // Trigger bubbles occasionally
      if (Math.random() > 0.9) createBubbles();

      // Check for specific gesture (optional: count extended fingers)
      // For now, any hand visibility triggers the cat
      statusText.innerText = "SCUBA CAT AKTİF!";
    } else {
      detectionDot.classList.remove("active");
      scubaCatContainer.classList.remove("active");
      statusText.innerText = "El Bekleniyor...";
      // Hide after animation
      setTimeout(() => {
        if (!scubaCatContainer.classList.contains("active")) {
          scubaCatContainer.classList.add("hidden");
        }
      }, 800);
    }
    
    canvasCtx.restore();
  }
  
  if (handLandmarker) {
    window.requestAnimationFrame(predictWebcam);
  }
}
