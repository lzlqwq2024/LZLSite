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
        /* 验证成功后取消按钮禁用，同时更改访问页面次数 */
        document.getElementById('submit-button').disabled = false;
        var temp = document.createElement('form');
        temp.action = '/login/login/';
        temp.method = 'POST';
        temp.style.display = 'none';
        var opt = document.createElement('textarea');
        opt.name = 'turn_visit_num';
        opt.value = 1;
        temp.appendChild(opt);
        document.body.appendChild(temp);

        var opt1 = document.createElement('textarea');
        opt1.name = 'username';
        var username = document.getElementById("username-input").value
        opt1.value = username;
        temp.appendChild(opt1);

        var opt2 = document.createElement('textarea');
        opt2.name = 'password';
        var password = document.getElementById("password-input").value
        opt2.value = password;
        temp.appendChild(opt2);

        var csrftoken = document.createElement("input");
        csrftoken.type= "hidden";
        csrftoken.name = "csrfmiddlewaretoken";
        csrftoken.value = document.getElementsByName('csrfmiddlewaretoken')[0].value;
        temp.appendChild(csrftoken);

        temp.submit();
    },
    error: function(){
    },
});