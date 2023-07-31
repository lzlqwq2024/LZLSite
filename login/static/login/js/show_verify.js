$('#mpanel1').slideVerify({
    type: 1,
    vOffset: 5,
    vSpace: 5,
    imgSize: {
        width: '100%',
        height: '200px',
    },
    blockSize: {
        width: '40px',
        height: '40px',
    },
    barSize: {
        width: '360px',
        height: '40px',
    },
    ready: function(){
    },
    success: function(){
        document.getElementById('submit-button').disabled = false;
    },
    error: function(){
    },
});