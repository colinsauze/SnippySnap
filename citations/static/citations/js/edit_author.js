var testing;
edit_author = (function () {

	var addEventHandlers, updateIdentifier, biblindexIdentifiersCount, bibliaPatristicaIdentifiersCount, addBiblindexIdentifiers, addBibliaPatristicaIdentifiers;
	var loadData, prepareForm;

	//----------------Private variables----------------
	biblindexIdentifiersCount = 0;
	bibliaPatristicaIdentifiersCount = 0;

	//----------------BEGIN PRIVATE METHODS----------------

	addEventHandlers = function () {
		edit.addEventHandlers('author');
		$('#add_biblindex_identifiers').on('click', function (event) {
			addBiblindexIdentifiers();
    	});
		$('#add_biblia_patristica_identifiers').on('click', function (event) {
			addBibliaPatristicaIdentifiers();
    	});
	};

//	//TODO: not sure we need identifiers once everything settles down (they are important for links now)
//	//if we keep them for safety we do not need them to be url safe anymore
//	updateIdentifier = function () {
//		document.getElementById('identifier').value = utils.getIdSafeString(document.getElementById('abbreviation').value);
//	};

	//these next two functions are duplicated in edit_work.js as I wanted them to have separate counts and putting it
	//all in a shared file would have shared the counters which worried me!
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
		var i;
		//deal with adding and populating generated fields
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
		edit.loadData(model, data) //you can add a list of fields to disable as a third argument if needed
		addEventHandlers();
	};

	prepareForm = function (model, data) {
		addBiblindexIdentifiers();
		addBibliaPatristicaIdentifiers();
		edit.prepareForm(model, data);
		addEventHandlers();
	};

	//----------------END PUBLIC METHODS----------------
	if (testing === true) {
		return {
			addBibliaPatristicaIdentifiers: addBibliaPatristicaIdentifiers,
			addBiblindexIdentifiers: addBiblindexIdentifiers,
			loadData: loadData,
			prepareForm: prepareForm,
			};
	} else {
		return {
			loadData: loadData,
			prepareForm: prepareForm,
			};
	}



} () );
