document.addEventListener("DOMContentLoaded", async function () {
    const img = document.getElementById("cameraStream");
    const model = await cocoSsd.load();
    console.log("COCO-SSD model loaded.");

    setInterval(async () => {
        const predictions = await model.detect(img);
        console.clear();
        predictions.forEach(prediction => {
            console.log(`Detected: ${prediction.class} (${Math.round(prediction.score * 100)}%)`);
        });
    }, 1000);
});

// Toggle Play/Pause (For future video streaming implementation)
function togglePlayPause() {
    alert("Live feed is always on!");
}

// Toggle Mute (Not applicable for image feed)
function toggleMute() {
    alert("No audio in live image stream!");
}
