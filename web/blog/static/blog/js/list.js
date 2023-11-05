$(function () {
    getList()
});

function getList() {
    $.ajax({
        url: '/api/v1/article/list/',
        type: 'get',
        success: getListSuccessHandler,
        error: getListErrorHandler,
    })
}

console.log('blog-list')

function getListSuccessHandler(data) {
    console.log('success', data)
}
  
function getListErrorHandler(data) {
    console.log('error', data)
}
