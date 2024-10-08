var content;

// 不能用translate作为函数名，可能是因为会与模板混起来！！！
function change() {
    // window.alert("adaf")
    // 获取textarea元素
    var textarea = document.getElementById('Source');
    // 获取textarea的内容
    content = textarea.value;

    // 获取源语言类型和目标语言类型
    var source_lang = document.getElementById('source_lang').value;
    var target_lang = document.getElementById('target_lang').value;

    // 通过jquery的Ajax请求发送到后端处理
    $.ajax({
        url: 'trans/',
        async: true,
        type: 'POST',
        data: {
            'source_lang': source_lang,
            'target_lang': target_lang,
            'content': content,
            // Forbidden（CSRF）方法：加上下面这一句
            "csrfmiddlewaretoken": $("[name='csrfmiddlewaretoken']").val(),
        },
        success: function (response) {
            // 将翻译结果由只读改为可写，以便可以写入翻译结果
            if (document.getElementById('Target').readOnly) {
                document.getElementById('Target').readOnly = false;  // 或者使用 targetTextarea.removeAttribute('readonly');
            }
            // 后端返回JSON对象：{result: "翻译后的文本"}
            document.getElementById('Target').value = response.result;
            // 将翻译后的结果改为只读
            document.getElementById('Target').readOnly = true;
        },
        error: function (data) {
            alert("翻译失败");
            console.log(data);
        }
    });
}
