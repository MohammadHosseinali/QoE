
function record(){
  var videoElement = Array.from(
                                  document.getElementsByTagName("video")).filter(
                                  function (element){
                                    return element.clientHeight >0;
                                  }
                                )[0]

  var videoStream = videoElement.captureStream();
  // var videoStream = videoElement.mozCaptureStream();

  var mediaRecorder = new MediaRecorder(videoStream, {
    mimeType: 'video/mp4; codecs="avc1.64001E"' // H.264 for video, AAC for audio
  });

  var recordedChunks = [];
  mediaRecorder.ondataavailable = event => {
    if (event.data.size > 0) {
      recordedChunks.push(event.data);
    }
  };


  mediaRecorder.onstop = () => {
    const blob = new Blob(recordedChunks, {
      type: 'video/mp4'
    });

    const url = URL.createObjectURL(blob);
    const downloadElement = document.createElement('a');
    downloadElement.href = url;
    downloadElement.download = 'recorded/mp4';
    downloadElement.click();
  };

  mediaRecorder.start();

  // Stop recording after 5 seconds
  setTimeout(() => {
    mediaRecorder.stop();
  }, 5000);

};

record()
