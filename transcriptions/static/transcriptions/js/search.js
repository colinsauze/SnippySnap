
search = (function () {
	
//	//private
	var addSearchLine, seach_line_count;
//	
//	//public
	var initialise;
//	
//	//----------------BEGIN PRIVATE METHODS----------------
	search_line_count = 1;
	field_types = {};
//	autocompletes = {};
//
	//TODO: add != for all? backend works but will multiply options considerably
	relation_options = {'TextField': '<option value="equals">equals</option><option value="not_equal">is not equal</option><option value="starts_with">starts with</option><option value="ends_with">ends with</option><option value="contains" selected="selected">contains</option>',
						'IntegerField': '<option value="equals">equals</option><option value="not_equal">is not equal</option>', //TODO: gt and lt? range even
						'ArrayField': '<option value="equals">includes</option><option value="not_include">does not include</option>',
						'NullBooleanField': '<option value="equals">equals</option><option value="not_equal">is not equal</option>'
						};
	
	
	
	updateSearchLine = function (event) {
		var number, model, field_value;
		model = 'versereading';
		number = event.target.id.replace('field_select_', '');
		field_value = event.target.value;
		console.log(field_value)
		doUpdateSearchLine(model, field_value, number);
	};
	
	doUpdateSearchLine = function (model, field_value, line_number, form_values) {
		if (typeof form_values !== 'undefined') {
			document.getElementById('field_select_' + line_number).value = form_values[0];
			field_value = form_values[0];
		}
		document.getElementById('relation_select_' + line_number).innerHTML = relation_options[field_types[model][field_value]];
		if (typeof form_values !== 'undefined') {
			document.getElementById('relation_select_' + line_number).value = form_values[1];
		} else if (field_value === 'citation_text') {
			document.getElementById('relation_select_' + line_number).value = 'contains';
		}
		if (field_value.split('__').pop() === 'language') {
			document.getElementById('search_text_container_' + line_number).innerHTML = '<select class="search_text" id="search_text_' + line_number + '"><option value="grc">Greek</option><option value="lat">Latin</option></select>';	
		} else if (field_value.split('__').pop() === 'book_number') {
			document.getElementById('search_text_container_' + line_number).innerHTML = '<select class="search_text" id="search_text_' + line_number + '"/>';	
			if (typeof form_values !== 'undefined') {
				populateBiblicalBook('search_text_' + line_number, parseInt(form_values[2]));
			} else {
				populateBiblicalBook('search_text_' + line_number);
			}
		} else if (field_types[model][field_value] === 'NullBooleanField'){
			document.getElementById('search_text_container_' + line_number).innerHTML = '<select class="search_text" id="search_text_' + line_number + '"><option value="True">True</option><option value="False">False</option></select>';
		} else {
			document.getElementById('search_text_container_' + line_number).innerHTML = '<input type="text" class="search_text" id="search_text_' + line_number + '"/>';
		}
		if (typeof form_values !== 'undefined') {
			document.getElementById('search_text_' + line_number).value = form_values[2];
		}
//		if (['CharField', 'TextField'].indexOf(field_types[model][field_value]) !== -1) { //TODO: consider restricting to = and != and destroying when that changes probably okay to leave if not too slow
//			autocompletes['search_text_' + line_number] = new autoComplete({
//				selector:'input[id="search_text_' + line_number + '"]', 
//				minChars: 1,
//				source: function(term, response){
//					var criteria;
//					criteria = {};
//					criteria[field_value] =  term;
//					$.getJSON('/citations/' + model + '/searchvalues', criteria, function(data) {
//						response(data);
//					});
//				},
//				renderItem: function (item) {
//					return '<div class="autocomplete-suggestion" data-val="' + item + '">' +  item + '</div>';
//				}
//			});
//		} else {
//			if (autocompletes.hasOwnProperty('search_text_' + line_number)) {
//				autocompletes['search_text_' + line_number].destroy();
//				delete autocompletes['search_text_' + line_number];
//			}
//				
//			
//		}
	};
	

	
	addSearchLine = function (field_select, value_select) {
		var i, div, optns, form_values, model, field_data;
		model = 'versereading';
		div = document.createElement('div');
		div.id = 'search_line_' + search_line_count;
		div.className = 'search_line';
		div.innerHTML = '<select id="field_select_' + search_line_count + '" class="field_select"></select>'
			+ '<select id="relation_select_' + search_line_count + '" class="relation_select"></select>'
			+ '<span id="search_text_container_' + search_line_count + '"><input class="search_text" type="text" id="search_text_' + search_line_count + '"></input></span>'
			+ '<img class="delete_logo" height="20px" width="20px" id="delete_search_line_'
			+ search_line_count + '" title="Delete this dependency" src="' + staticUrl + 'citations/images/delete.png"/>';
		document.getElementById('search_lines_div').appendChild(div);
		field_data = [{"position": 0, "label": "Text", "field_type": "TextField", "id": "reading_text"},
		              {"position": 1, "label": "Chapter number", "field_type": "IntegerField", "id": "verse__chapter_number"},
		              {"position": 2, "label": "Verse number", "field_type": "IntegerField", "id": "verse__verse_number"}
		                     ]
	//forms.populateSelect(field_data, document.getElementById('field_select_' + search_line_count), {'value_key': 'id', 'text_keys': 'label', 'selected': 'reading_text'});
		//console.log(document.getElementById('field_select_' + search_line_count).innerHTML)
		optns = [];
		if (!field_types.hasOwnProperty(model)) {
			field_types[model] = {}
		}
		for (i = 0; i < field_data.length; i += 1) {
			field_types[model][field_data[i].id] = field_data[i].field_type
			optns.push('<option value="' + field_data[i].id + '">' + field_data[i].label + '</option>');
		}
		document.getElementById('field_select_' + search_line_count).innerHTML = optns.join('');
		//use the default field to set the first search line options
		if (typeof field_select !== 'undefined') {
			//we need to populate data at the same time
			form_values = deconstructQueryElement(field_select, value_select);
			doUpdateSearchLine(model, field_data[0].id, search_line_count, form_values);
		} else {
			doUpdateSearchLine(model, field_data[0].id, search_line_count);
		}
		$('#field_select_' + search_line_count).on('change', function(event) {
			updateSearchLine(event);
		});
		$('#delete_search_line_' + search_line_count).on('click', function (event) {
			event.target.parentNode.parentNode.removeChild(event.target.parentNode);
		});
		search_line_count += 1;
	};
	
	deconstructQueryElement = function(field, value) {
		var relation;
		value = value.replace(/\+/g, ' ')
		value = decodeURIComponent(value);
		//remove the case insensitive marker (these are automated so we don't need to reflect it in the interface)
		if (/.+?\|i$/.test(value)) {
			value = value.replace('|i', '');
		}
		relation = 'equals'; //default
		if (/^\*.+\*$/.test(value)) {
			relation = 'contains';
			value = value.replace(/\*/g, '');
		} else if (/^.+\*$/.test(value)) {
			relation = 'starts_with';
			value = value.replace(/\*/g, '');
		} else if (/^\*.+$/.test(value)) {
			relation = 'ends_with';
			value = value.replace(/\*/g, '');
		} else if (/^!.+$/.test(value)) {
			relation = 'not_equal';
			value = value.replace(/!/g, '');
		}
		return [field, relation, value];
	}
	
	constructQueryElement = function (model, field, relation, value) {
		var field_type, case_insensitive;
		case_insensitive = false;
		field_type = field_types[model][field];
		if (field_type === 'CharField' || field_type === 'TextField') {			
			case_insensitive = true;
		}
		if (relation === 'contains') {
			value = '*' + value + '*';
		} else if (relation === 'starts_with') {
			value = value + '*';
		} else if (relation === 'ends_with') {
			value = '*' + value;
		} else if (relation === 'not_equal') {
			value = '!' + value;
		}
		if (case_insensitive === true) {
			value = value + '|i';
		}
		value = encodeURIComponent(value);
		return field + '=' + value;
	};
	
	beginSearch = function (search_type) {
		var i, query_list, field, relation, value, query_string, model;
		model = 'versereading';
		query_list = ['_sort=verse__context,verse__siglum&project=ECM_04'];
		for (i = 0; i < search_line_count; i += 1) {
			if (document.getElementById('search_text_' + i) && document.getElementById('search_text_' + i).value !== '') {
				field = document.getElementById('field_select_' + i).value;
				relation = document.getElementById('relation_select_' + i).value;
				value = document.getElementById('search_text_' + i).value;
				query_list.push(constructQueryElement(model, field, relation, value));
			}
		}
		query_string = query_list.join('&');
		history.pushState({}, 'search',  '?model=' + model + '&'  + query_string);
		location.href = '/transcriptions/results/?' + query_string;		
	};
//	

//	
//	setupQuickSearchForm = function () {
//		var book, query;
//		query = utils.getCurrentQuery();
//		book = 'none';
//		if (query.hasOwnProperty('model')) {
//			if (query.hasOwnProperty('biblical_work__book_number')) {
//				book = parseInt(query.biblical_work__book_number);
//			}
//			if (query.hasOwnProperty('chapter')) {
//				document.getElementById('chapter_input').value = query.chapter;
//			} else {
//				document.getElementById('chapter_input').value = '';
//			}
//			if (query.hasOwnProperty('verse')) {
//				document.getElementById('verse_input').value = query.verse;
//			} else {
//				document.getElementById('verse_input').value = '';
//			}	
//			if (query.hasOwnProperty('language')) {
//				document.getElementById('language_select').value = query.language;
//			} 
//		}
//		populateBiblicalBook('book_select', book);
//	};
//	
//	populateBiblicalBook = function (select_id, selected) {
//		var criteria;
//		criteria = {'limit': 1000000, '_sort': 'book_number', 'book_number': '4,6,7,8,9,10,11,12,13,145,15,16,17,18,19', 'corpus': 'NT'};
//        utils.getItemsFromDatabase('transcriptions', 'work', criteria, 'GET', function (data) {
//    		forms.populateSelect(data.results, document.getElementById(select_id), {'value_key': 'book_number', 'text_keys': 'name', 'selected': selected}); 
//    	});
//	};
	
	resetForm = function () {
		var i, div;
		for (i = 1; i <= search_line_count; i += 1) {
			div = document.getElementById('search_line_' + i);
			if (div) {
				div.parentNode.removeChild(div);
			}
		}
		search_line_count = 1;
	};
	
	setupSearchForm = function () {
		resetForm();
		query = utils.getCurrentQuery();
		line_added = false;
		if (query.hasOwnProperty('model')) {
			for (key in query) {
				if (query.hasOwnProperty(key) && key !== 'model' 
						&& key !== '_sort'
						&& key !== 'project') {
					addSearchLine(key, query[key]);
					line_added = true;
				}
			}
			if (!line_added) {
				addSearchLine();
			}
		} else {
			addSearchLine();
		}
	};
	
	//----------------END PRIVATE METHODS----------------
	
	//----------------BEGIN PUBLIC METHODS----------------
	
	initialise = function (search_type) {
		//for simple search
    	var book, criteria, query, book, key, line_added, my_autocomplete;
    	
		setupSearchForm();
		
		//add handler for adding more search lines
    	$('#add_search_line').off('click.add_line');
		$('#add_search_line').on('click.add_line', function () {
			addSearchLine();
		});
		//add handler for search
    	$('#search_button').off('click.search');
		$('#search_button').on('click.search', function () {
			beginSearch();
		});
		$('#reset_button').off('click.reset');
		$('#reset_button').on('click.reset', function () {
			resetForm();
			addSearchLine();
		});
	};
	

	
	//----------------END PUBLIC METHODS----------------

	return {
				initialise: initialise,
			};
	
	
	
} () );
