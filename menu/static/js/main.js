var waitingDialog = waitingDialog || (function ($) {
	'use strict';
	var $dialog = $('<div class="modal fade" data-backdrop="static" data-keyboard="false" tabindex="-1" role="dialog" aria-hidden="true" style="padding-top:15%; overflow-y:visible;">' +
		'<div class="modal-dialog modal-m">' +
			'<div class="modal-content">' +
				'<div class="modal-header"><h3 style="margin:0;"></h3>' +
				'</div>' +
				'<div class="modal-body">' +
					'<div class="progress progress-striped active" style="margin-bottom:0;"><div class="progress-bar" style="width: 100%">' +
					'</div>' +
				'</div>' +
			'</div>' +
		'</div>' +
	'</div>');

	return {
		show: function (mensaje) {
			$dialog.find('.modal-dialog').attr('class', 'modal-dialog').addClass('modal-m');
			$dialog.find('.progress-bar').attr('class', 'progress-bar');
			$dialog.find('.progress-bar').addClass('progress-bar-striped').addClass('progress-bar-animated');
			$dialog.find('h3').text(mensaje);
			$dialog.modal();
		},
		hide: function () {
			$dialog.modal('hide');
		}
	};

})(jQuery);

function crear_arbol(arbol) {
	var $searchableTree = $('#treeview-searchable').treeview({
		data: arbol
	});
	var search = function(e) {
		var pattern = $('#input-search').val();
        	var options = {
			ignoreCase: true,
            		exactMatch: false,
            		revealResults: true
        	};
        	var results = $searchableTree.treeview('search', [ pattern, options ]);
        	$('#search-output').html(output);
    	}
	$('#btn-search').on('click', search);
	$('#input-search').on('keyup', search);
	$('#btn-clear-search').on('click', function (e) {
		$searchableTree.treeview('clearSearch');
		$('#input-search').val('');
		$('#search-output').html('');
	});
	var initSelectableTree = function() {
		return $('#treeview-selectable').treeview({
			data: arbol,
			multiSelect: true
	  });
	};
	var $selectableTree = initSelectableTree();
	var findAllNodes = function() {
		return $selectableTree.treeview('search', [ '\\w+', { ignoreCase: true, exactMatch: false } ]);
	};
	var findSelectableNodes = function() {
		return $selectableTree.treeview('search', [ $('#input-select-node').val(), { ignoreCase: true, exactMatch: false } ]);
	};
	var allNodes = findAllNodes();
	var selectableNodes = findSelectableNodes();
	$('#btn-select-node.select-node').on('click', function (e) {
		selectableNodes = findSelectableNodes();
		$('.select-node').prop('disabled', !(selectableNodes.length >= 1));
		$selectableTree.treeview('unselectNode', [ allNodes, { silent: $('#chk-select-silent').is(':checked') }]);
		$selectableTree.treeview('selectNode', [ selectableNodes, { silent: $('#chk-select-silent').is(':checked') }]);
	});
	$('#btn-unselect-node.select-node').on('click', function (e) {
		$selectableTree.treeview('unselectNode', [ allNodes, { silent: $('#chk-select-silent').is(':checked') }]);
		$selectableTree.treeview('collapseAll');
	});
	$selectableTree.treeview('collapseAll');
}

function anidar(arbol) {
	arbol_for = [];
	$.each(arbol, function(i, val) {
		arbol_for.push({
			text: i
		});
		$.each(arbol, function(i_2, val_2) {
			if(val[0] == val_2[1]) {
				if(typeof arbol_for[arbol_for.length - 1]['nodes'] === 'undefined') {
					arbol_for[arbol_for.length - 1]['nodes'] = JSON.parse('[{ "text":"' + i_2 + '" }]');
				} else {
					arbol_for[arbol_for.length - 1]['nodes'].push({
						text: i_2
					})
				}
			}
		});
		if(typeof arbol_for[arbol_for.length - 1]['nodes'] === 'undefined') {
			arbol_for.splice(arbol_for.length - 1);
		}
	});
	crear_arbol(JSON.stringify(arbol_for));
}

function traer_facultades_ajax() {
	$.ajax({
		url : "taller_1/traer_facultades",
		type : "POST",
		data : { valor: 'TRAER_FACULTADES' },
		success : function(ret) {
			setTimeout(function() {waitingDialog.hide();}, 1000);
			anidar(ret);
		},
		error : function(xhr,errmsg,err) {
			console.log(xhr.status + ": " + xhr.responseText);
		}
	});
}

jQuery(document).ready(function() {
	$('#traer_facultades').on('click', function(event){
		event.preventDefault();
		waitingDialog.show('Procesando crawler...');
		traer_facultades_ajax();
	});
});
