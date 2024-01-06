src = "../../static/js/socket.io.js";
src = "../../static/js/toastr.min.js";

class toastr_filter {

    constructor(filter_group) {
        this.filter_group = filter_group;

        const socket = io();
        socket.on(filter_group, function(data) {
            console.log(data)
            // Check the type of notification
            switch(data.type) {
                case 'success':
                case true:
                    toastr.success(data.message);
                    break;
                case 'error':
                case false:
                    toastr.error(data.message);
                    break;
                case 'info':
                    toastr.info(data.message);
                    break;
                case 'warning':
                    toastr.warning(data.message);
                    break;
                default:
                    toastr.info(data.message); // Default case
            }
        });

    }
}


toastr.options = {
    "closeButton": true,
    "debug": false,
    "newestOnTop": false,
    "progressBar": false,
    "positionClass": "toast-bottom-right",
    "preventDuplicates": false,
    "onclick": null,
    "showDuration": "300",
    "hideDuration": "1000",
    "timeOut": "5000",
    "extendedTimeOut": "1000",
    "showEasing": "swing",
    "hideEasing": "linear",
    "showMethod": "fadeIn",
    "hideMethod": "fadeOut"
}
