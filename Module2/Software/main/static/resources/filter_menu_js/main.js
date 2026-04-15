(function($) {

	"use strict";


	var el = document.querySelectorAll("[id*='multiple-checkboxes']");

	 $(document).ready(function() {
        el.forEach(element => $("#"+element.id).multiselect({
          includeSelectAllOption: true,
        }));
    });
	 
})(jQuery);
