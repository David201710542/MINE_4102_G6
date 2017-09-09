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

function anidar_p2(leaf, root) {
	retorno = []
	for(y in root) {
		retorno.push(root[y]);
		for(x in leaf) {
			if(root[y]['origen'].join('/') == '0' && leaf[x]['origen'].slice(-1).join('/') == root[y].orden) {
				if(typeof retorno[retorno.length - 1]['nodes'] === 'undefined') {
					retorno[retorno.length - 1]['nodes'] = [];
				}
				retorno[retorno.length - 1]['nodes'].push(leaf[x])
			}
			else if(root[y]['origen'].join('/') == leaf[x]['origen'].slice(0, -1).join('/') && leaf[x]['origen'].slice(-1).join('/') == root[y].orden) {
				if(typeof retorno[retorno.length - 1]['nodes'] === 'undefined') {
					retorno[retorno.length - 1]['nodes'] = [];
				}
				retorno[retorno.length - 1]['nodes'].push(leaf[x])
			}
		}
	}
	return retorno;
}

function anidar(arbol) {
	arbol_leaf = [];
	arbol_root = [];
	max_llave = 0;
	num_veces = 0;
	$.each(arbol, function(i, val) {
		if(val[4] > max_llave) { max_llave = val[4]; }
	});
	for(var i = max_llave; i >= 2; i--) {
		arbol_root = [];
		for(var x in arbol) {
			if(arbol[x][4] == i && num_veces == 0) {
				arbol_leaf.push({
					text: x,
					orden: arbol[x][2],
					origen: arbol[x][3].toString().split("-")
				});
			}
			if(arbol[x][4] == i - 1) {
				arbol_root.push({
					text: x,
					orden: arbol[x][2],
					origen: arbol[x][3].toString().split("-")
				});
			}
		}
		num_veces = 1;
		arbol_leaf = anidar_p2(arbol_leaf, arbol_root);
	}
	var i = arbol_leaf.length;
	while(i--) {
		if(typeof arbol_leaf[i]['nodes'] === 'undefined') {
			arbol_leaf.splice(i, 1);
		}
	}
	crear_arbol(arbol_leaf);
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
			setTimeout(function() {waitingDialog.hide();}, 1000);
			alert(xhr.status + ": " + xhr.responseText);
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
