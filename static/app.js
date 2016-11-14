user_name = 'bornofawesomeness';
var api_url = window.location.protocol + '//' + window.location.hostname + '/retrieve'
var app = new Vue({
    el: '#app',
    data: {
        playlists: {}
    }
});
uri = '/retrieve?uid=bornofawesomeness&playlists=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14'
$.getJSON(uri).then(function(data) {
    console.log(data);
    Vue.set(app, 'playlists', data.contents)
});