jQuery(document).ready(function () {
    for ( tabid in window.plugin_dataTables || {} ) {
        var attr = window.plugin_dataTables[tabid];
        window.plugin_dataTables[tabid] = jQuery('#'+tabid).dataTable( attr );
    }
})