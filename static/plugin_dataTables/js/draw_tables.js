
/*  ~ LICENCE NOTES ~
 *
 *  This file is part of plugin_dataTables.
 *
 *  plugin_dataTables is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  plugin_dataTables is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with plugin_dataTables. If not, see <http://www.gnu.org/licenses/>.
 *
 */

jQuery(document).ready(function () {
    for ( tabid in window.plugin_dataTables || {} ) {
        var attr = window.plugin_dataTables[tabid];
        window.plugin_dataTables[tabid] = jQuery('#'+tabid).dataTable( attr );
    }
})