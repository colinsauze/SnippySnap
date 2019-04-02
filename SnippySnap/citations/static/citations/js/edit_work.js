var testing
edit_work = (function () {

	var addEventHandlers, updateIdentifier, addBiblindexIdentifiers, addBibliaPatristicaIdentifiers, biblindexIdentifiersCount,
		bibliaPatristicaIdentifiersCount, authorsCount, addAuthors;
	var loadData, prepareForm;

	//----------------Private variables----------------
	authorsCount = 0;
	biblindexIdentifiersCount = 0;
	bibliaPatristicaIdentifiersCount = 0;

	//----------------BEGIN PRIVATE METHODS----------------

	addEventHandlers = function () {
		edit.addEventHandlers('work');
		$('#add_authors').on('click', function (event) {
			addAuthors();
    	});
		$('#add_biblindex_identifiers').on('click', function (event) {
			addBiblindexIdentifiers();
    	});
		$('#add_biblia_patristica_identifiers').on('click', function (event) {
			addBibliaPatristicaIdentifiers();
    	});
		$('#author').on('change', function (event) {
			//see if its obsolete and if so check obsolete box for work
			api.getItemFromDatabasePromise('citations', 'author', event.target.value).then(function (data) {
				if (data.obsolete === true) {
					document.getElementById('obsolete').checked = true;
				} else {
					document.getElementById('obsolete').checked = false;
				}
			});
		});
	};


	//TODO: think about whether the author assigned in the 'author' category should be visible in the drop down or not
	addAuthors = function (select_value) {
		var newDiv, html, criteria, select_id;
		html = [];
		newDiv = document.createElement('div');
		html.push('<select id="other_possible_authors_');
		html.push(authorsCount + '" name="other_possible_authors_');
		html.push(authorsCount + '" class="integer"></select>');
		html.push('<img class="delete_logo" height="20px" width="20px" id="delete_authors_');
    	html.push(authorsCount + '" title="Delete this author" src="' + staticUrl + '/citations/images/delete.png"/>');
    	newDiv.innerHTML = html.join('');
		document.getElementById('other_possible_authors').appendChild(newDiv);
		criteria = {'limit': 1000000, 'language': cits.project.language, '_sort': 'abbreviation', '_fields': 'id,abbreviation,full_name,obsolete'};
		//get data and populate select
		select_id = 'other_possible_authors_' + authorsCount;
    	api.getItemsFromDatabasePromise('citations', 'author', criteria).then(function (data) {
    		forms.populateSelect(data.results,
    							document.getElementById(select_id),
    							{'value_key': 'id',
    							 'text_keys': {1 : 'abbreviation', 2 : 'full_name'},
    							 'selected': select_value,
    							 'add_class': {'data_key': 'obsolete', 'data_value': true, 'class_name': 'obsolete'}});
    		if (typeof callback !== 'undefined') {
    			callback();
    		}
    	});
		$('#delete_authors_' + authorsCount).on('click', function (event) {
    		deleteElement(event.target.parentNode);
    	});
		authorsCount += 1;
	};

	//these next two functions are duplicated in edit_author.js as I wanted them to have separate counts and putting it
	//all in a shared file would have shared the counters which worried me more than the duplication
	addBiblindexIdentifiers = function (data) {
		/*add a biblindex identifier box to fill in */
		var newDiv, html;
		html = [];
		newDiv = document.createElement('div');
		html.push('<input type="text" id="biblindex_identifiers_');
		html.push(biblindexIdentifiersCount + '" name="biblindex_identifiers_')
		html.push(biblindexIdentifiersCount + '"/>');
		html.push('<img class="delete_logo" height="20px" width="20px" id="delete_biblindex_identifiers_');
    	html.push(biblindexIdentifiersCount + '" title="Delete this identifier" src="' + staticUrl + '/citations/images/delete.png"/>');
    	newDiv.innerHTML = html.join('');
		document.getElementById('biblindex_identifiers').appendChild(newDiv);
		if (data) {
			document.getElementById('biblindex_identifiers_' + biblindexIdentifiersCount).value = data;
		}
		$('#delete_biblindex_identifiers_' + biblindexIdentifiersCount).on('click', function (event) {
    		deleteElement(event.target.parentNode);
    	});
		biblindexIdentifiersCount += 1;
	};

	addBibliaPatristicaIdentifiers = function (data) {
		/*add a biblia patristica identifier box to fill in */
		var newDiv, html;
		html = [];
		newDiv = document.createElement('div');
		html.push('<input type="text" id="biblia_patristica_identifiers_');
		html.push(bibliaPatristicaIdentifiersCount + '" name="biblia_patristica_identifiers_');
		html.push(bibliaPatristicaIdentifiersCount + '"/>');
		html.push('<img class="delete_logo" height="20px" width="20px" id="delete_biblia_patristica_identifiers_');
    	html.push(bibliaPatristicaIdentifiersCount + '" title="Delete this identifier" src="' + staticUrl + '/citations/images/delete.png"/>');
    	newDiv.innerHTML = html.join('');
		document.getElementById('biblia_patristica_identifiers').appendChild(newDiv);
		if (data) {
			document.getElementById('biblia_patristica_identifiers_' + bibliaPatristicaIdentifiersCount).value = data;
		}
		$('#delete_biblia_patristica_identifiers_' + bibliaPatristicaIdentifiersCount).on('click', function (event) {
    		deleteElement(event.target.parentNode);
    	});
		bibliaPatristicaIdentifiersCount += 1;
	};

	//----------------END PRIVATE METHODS----------------

	//----------------BEGIN PUBLIC METHODS----------------

	loadData = function (model, data) {
		var author;
		console.log(JSON.stringify(data));
		author = data.author;
		//dynamically created select fields need to be disabled in callback
		//as the data is not ready in time for them to be disabled in
		//the loadData function
		edit.populateAuthor(model, {'select': author});
		//deal with adding and populating generated fields
		if (data.other_possible_authors.length > 0) {
			for (i = 0; i < data.other_possible_authors.length; i += 1) {
				addAuthors(data.other_possible_authors[i]);
			}
		} else {
			addAuthors();
		}
		if (data.biblindex_identifiers !== null) {
			for (i = 0; i < data.biblindex_identifiers.length; i += 1) {
				addBiblindexIdentifiers(data.biblindex_identifiers[i]);
			}
		} else {
			addBiblindexIdentifiers();
		}
		if (data.biblia_patristica_identifiers !== null) {
			for (i = 0; i < data.biblia_patristica_identifiers.length; i += 1) {
				addBibliaPatristicaIdentifiers(data.biblia_patristica_identifiers[i]);
			}
		} else {
			addBibliaPatristicaIdentifiers();
		}
		edit.loadData(model, data)
		addEventHandlers();
	};

	prepareForm = function (model, data) {
		edit.populateAuthor(model);
		addAuthors();
		addBiblindexIdentifiers();
		addBibliaPatristicaIdentifiers();
		edit.prepareForm(model, data);
		addEventHandlers();
	};

	//----------------END PUBLIC METHODS----------------
	if (testing === true) {
		return {
				loadData: loadData,
				prepareForm: prepareForm,
				addAuthors: addAuthors,
				addBibliaPatristicaIdentifiers: addBibliaPatristicaIdentifiers,
				addBiblindexIdentifiers: addBiblindexIdentifiers
				};
	} else {
		return {
			loadData: loadData,
			prepareForm: prepareForm
			};
	}


} () );
