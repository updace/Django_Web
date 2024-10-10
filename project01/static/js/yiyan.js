function sub(){
    var question = document.getElementById("Question").value;

    // document.getElementById("Question").value = "";
    // window.alert("aaa");
    document.getElementById("Answer").setAttribute("placeholder","正在生成"+question+"的回答，请稍等...");

    // 要使用jquery的ajax的化要在html里导入对应的包，不然ajax不运行
    $.ajax({
        url: '/ai/Aians/',
        async: true,
        type: 'POST',
        data: {
            'question': question,
            // Forbidden（CSRF）方法：加上下面这一句
            "csrfmiddlewaretoken": $("[name='csrfmiddlewaretoken']").val(),
        },
        headers: { "X-CSRFToken": "{{ csrf_token }}" },
        success: function (response) {
            // alert("成功！！");
            // 将翻译结果由只读改为可写，以便可以写入翻译结果
            if (document.getElementById('Answer').readOnly) {
                document.getElementById('Answer').readOnly = false;  // 或者使用 targetTextarea.removeAttribute('readonly');
            }

            var result=response.result.replace(/<[^>]+>/g, '');

            // 后端返回JSON对象：{result: "翻译后的文本"}
            document.getElementById('Answer').value = result;
            // 将翻译后的结果改为只读
            document.getElementById('Answer').readOnly = true;
        },
        error: function (data) {
            alert("回答失败");
            console.log(data);
        }
    });
}