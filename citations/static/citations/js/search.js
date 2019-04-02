
search = (function () {

	//private
	var doAddSearchLine, seach_line_count, addSearchLine, switchSearchType, field_data;

	//public
	var initialise;

	//----------------BEGIN PRIVATE METHODS----------------
	search_line_count = 1;
	field_types = {};
	autocompletes = {};

	//TODO: add != for all? backend works but will multiply options considerably
	relation_options = {'TextField': '<option value="equals">equals</option><option value="not_equal">is not equal</option><option value="starts_with">starts with</option><option value="ends_with">ends with</option><option value="contains">contains</option>',
						'IntegerField': '<option value="equals">equals</option><option value="not_equal">is not equal</option>', //TODO: gt and lt? range even
						'ArrayField': '<option value="equals">includes</option><option value="not_include">does not include</option>',
						'NullBooleanField': '<option value="equals">equals</option><option value="not_equal">is not equal</option>'
						};

	switchSearchType = function () {
		if (document.getElementById('advanced_search_form').style.display === 'none') {
			document.getElementById('quick_search_form').style.display = 'none';
			document.getElementById('advanced_search_form').style.display = 'block';
			setupAdvancedSearchForm();
		} else {
			document.getElementById('advanced_search_form').style.display = 'none';
			document.getElementById('quick_search_form').style.display = 'block';
			setupQuickSearchForm();
		}
	};

	doAddSearchLine = function (model, field_data, field_select, value_select) {
		var i, div, optns, form_values;

		div = document.createElement('div');
		div.id = 'search_line_' + search_line_count;
		div.className = 'search_line';
		div.innerHTML = '<select id="field_select_' + search_line_count + '" class="field_select"></select>'
			+ '<select id="relation_select_' + search_line_count + '" class="relation_select"></select>'
			+ '<span id="search_text_container_' + search_line_count + '"><input class="search_text" type="text" id="search_text_' + search_line_count + '"></input></span>'
			+ '<img class="delete_logo" height="20px" width="20px" id="delete_search_line_'
			+ search_line_count + '" title="Delete this dependency" src="' + staticUrl + 'citations/images/delete.png"/>';
		document.getElementById('search_lines_div').appendChild(div);
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
		//add event handlers
		$('#field_select_' + search_line_count).on('change', function(event) {
			updateSearchLine(event);
		});
		$('#delete_search_line_' + search_line_count).on('click', function (event) {
			event.target.parentNode.parentNode.removeChild(event.target.parentNode);
		});

		search_line_count += 1;
	};

	updateSearchLine = function (event) {
		var number, model, field_value;
		model = document.getElementById('model_select').value;
		number = event.target.id.replace('field_select_', '');
		field_value = event.target.value;
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
		} else if (field_value.split('__').pop() === 'identifier') {
			document.getElementById('search_text_container_' + line_number).innerHTML = '<select class="search_text" id="search_text_' + line_number + '"/>';
			if (typeof form_values !== 'undefined') {
				populateBiblicalBook('search_text_' + line_number, form_values[2]);
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
		if (['CharField', 'TextField'].indexOf(field_types[model][field_value]) !== -1) { //TODO: consider restricting to = and != and destroying when that changes probably okay to leave if not too slow
			autocompletes['search_text_' + line_number] = new autoComplete({
				selector:'input[id="search_text_' + line_number + '"]',
				minChars: 1,
				source: function(term, response){
					var criteria;
					criteria = {};
					criteria[field_value] =  term;
					$.getJSON('/citations/' + model + '/searchvalues', criteria, function(data) {
						response(data);
					});
				},
				renderItem: function (item) {
					return '<div class="autocomplete-suggestion" data-val="' + item + '">' +  item + '</div>';
				}
			});
		} else {
			if (autocompletes.hasOwnProperty('search_text_' + line_number)) {
				autocompletes['search_text_' + line_number].destroy();
				delete autocompletes['search_text_' + line_number];
			}


		}
	};

	addSearchLine = function (field_select, value_select) {
		var model, field_data;
		model = document.getElementById('model_select').value;
		field_data = [];
		if (model != 'none') {
			$.ajax({'url': '/citations/' + model + '/searchfields/', 'headers': {'Content-Type': 'application/json'}, 'method': 'GET',  'success': function (response) {
	    		field_data = response;
	    		doAddSearchLine(model, field_data, field_select, value_select);
	    	}}).fail(function (response) {
	    		doAddSearchLine(model, field_data, field_select, value_select);
	    	});
		}
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
			if (field.indexOf('abbreviation') === -1) {
				case_insensitive = true;
			}
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
		if (search_type === 'quick') {
			model = 'citation';
			query_list = [];
			if (document.getElementById('book_select').value !== 'none') {
				query_list.push('biblical_work__identifier=' + document.getElementById('book_select').value);
			}
			if (!isNaN(parseInt(document.getElementById('chapter_input').value))) {
				query_list.push('chapter=' + document.getElementById('chapter_input').value);
			}
			if (!isNaN(parseInt(document.getElementById('verse_input').value))) {
				query_list.push('verse=' + document.getElementById('verse_input').value);
			}
			if (document.getElementById('language_select').value !== 'none') {
				query_list.push('language=' + document.getElementById('language_select').value);
			}
		} else {
			model = document.getElementById('model_select').value;
			query_list = [];
			query_list.push('_advanced=true');
			for (i = 0; i < search_line_count; i += 1) {
				if (document.getElementById('search_text_' + i) && document.getElementById('search_text_' + i).value !== '') {
					field = document.getElementById('field_select_' + i).value;
					relation = document.getElementById('relation_select_' + i).value;
					value = document.getElementById('search_text_' + i).value;
					query_list.push(constructQueryElement(model, field, relation, value));
				}
			}
		}
		query_string = query_list.join('&');
		history.pushState({}, 'search',  '?model=' + model + '&'  + query_string);
		location.href = '/citations/' + model + '/results/?' + query_string;
	};

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

	setupQuickSearchForm = function () {
		var book, query;
		query = utils.getCurrentQuery();
		book = 'none';
		if (query.hasOwnProperty('model')) {
			if (query.hasOwnProperty('biblical_work__identifier')) {
				book = query.biblical_work__identifier;
			}
			if (query.hasOwnProperty('chapter')) {
				document.getElementById('chapter_input').value = query.chapter;
			} else {
				document.getElementById('chapter_input').value = '';
			}
			if (query.hasOwnProperty('verse')) {
				document.getElementById('verse_input').value = query.verse;
			} else {
				document.getElementById('verse_input').value = '';
			}
			if (query.hasOwnProperty('language')) {
				document.getElementById('language_select').value = query.language;
			}
		}
		populateBiblicalBook('book_select', book);
	};

	populateBiblicalBook = function (select_id, selected) {
		var criteria, books_with_citations;
		books_with_citations = ['John', 'Rom', '1Cor', '2Cor', 'Gal', 'Eph', 'Phil', 'Col', '1Thess', '2Thess', '1Tim', '2Tim', 'Titus', 'Phlm', 'Heb'];
		criteria = {'limit': 1000000, '_sort': 'sort_value', 'abbreviation': books_with_citations.join(','), 'collection__identifier': 'NT'};
        api.getItemsFromDatabasePromise('transcriptions', 'work', criteria).then(function (data) {
    		forms.populateSelect(data.results, document.getElementById(select_id), {'value_key': 'identifier', 'text_keys': 'name', 'selected': selected});
    	});
	};

	setupAdvancedSearchForm = function () {
		resetForm();
		query = utils.getCurrentQuery();
		if (query.hasOwnProperty('_advanced')) {
			delete query['_advanced'];
		}
		line_added = false;
		if (query.hasOwnProperty('model')) {
			document.getElementById('model_select').value = query.model;
			for (key in query) {
				if (query.hasOwnProperty(key) && key !== 'model') {
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
    	if (search_type == 'quick') {
    		setupQuickSearchForm();
    		//add handler for search
        	$('#quick_search_button').off('click.quick_search');
    		$('#quick_search_button').on('click.quick_search', function () {
    			beginSearch('quick');
    		});
    		$('#advanced_search').off('click.advanced');
    		$('#advanced_search').on('click.advanced', function () {
    			location.href = '/citations/search/advanced';
    		});

    	} else {
    		setupAdvancedSearchForm();

    		//add handler for model selection
    		$('#model_select').off('change.model_select');
    		$('#model_select').on('change.model_select', function () {
    			resetForm();
    			addSearchLine();
    		});
    		//add handler for adding more search lines
        	$('#add_search_line').off('click.add_line');
    		$('#add_search_line').on('click.add_line', function () {
    			addSearchLine();
    		});
    		//add handler for search
        	$('#advanced_search_button').off('click.advanced_search');
    		$('#advanced_search_button').on('click.advanced_search', function () {
    			beginSearch('advanced');
    		});
    		$('#quick_search').off('click.quick');
    		$('#quick_search').on('click.quick', function () {
    			location.href = '/citations/search';
    		});


    	}

	};



	//----------------END PUBLIC METHODS----------------

	return {
				initialise: initialise,
			};



} () );
