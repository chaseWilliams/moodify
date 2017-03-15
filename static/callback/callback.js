api_url = '/loading?uid='
app = new Vue({
    el: '#app',
    data: {
        lastfm: ''
    },
    methods: {
        save_username: function () {
            if (this.lastfm == '')
                lastfm_username = null
            else
                lastfm_username = this.lastfm
            data = {
                lastfm: this.lastfm,
                uid: user_name
            }
            data = JSON.stringify(data)
            $.ajax({
                type: 'POST',
                url: '/lastfm',
                headers: {'Content-Type': 'application/json'},
                dataType: 'json',
                data: data
            }).always(function(data) {
                console.log('awesome')
                window.location.href = api_url + user_name
            })
        }
    }
})