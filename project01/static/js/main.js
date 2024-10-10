function search()
{
    var question = document.getElementById('search').value;
    document.getElementById("search").value = "";
    // window.alert(question);

    $.ajax({
        url: '/main/s/',
        async: true,
        type: 'POST',
        data: {
            'question': question,
            // Forbidden（CSRF）方法：加上下面这一句
            "csrfmiddlewaretoken": $("[name='csrfmiddlewaretoken']").val(),
        },
        headers: { "X-CSRFToken": "{{ csrf_token }}" },
        success: function (response) {
            // alert("搜索成功")

        },
        error: function (response) {
            alert("搜索失败");
            // alert(response);
            // console.log(response);
        }
    });
}
