var testing;
edit_citation = (function () {

	//public functions
	var loadData, prepareForm;

	//private functions
	var displayExtras, displayClavis, populateTranscriber, populateBook, prepareEditionEntry, showEditionDetails,
		addEventHandlers, updateIdentifier, getBiblicalText, stripTags, getLanguage, addManuscriptVariants, addDependency,
		addCatena, addParallel, findEdition, getVerseReference;

	//private variables
	var dependencyCount, msVariantCount, catenaCount, parallelCount, sourceCount;

	//----------------Private variables----------------
	dependencyCount = 0;
	msVariantCount = 0;
	catenaCount = 0;
	parallelCount = 0;
	sourceCount = 0;


	//----------------BEGIN PRIVATE METHODS----------------

	populateTranscriber = function () {
		var date;
		document.getElementById('created_by').value = cits.user.id_string;
		date = new Date();
        document.getElementById('created_time').value = date.getTime();
        document.getElementById('created_time_display').value = date.getDate() + '/' + (date.getMonth() + 1) + '/' + date.getFullYear();
	};


	//TODO: this and project settings should perhaps be able to accommodate a range of books not just one or everything
	populateBook = function(options, callback) {
	  var book, criteria;
	  if (typeof options === 'undefined') {
	    options = {};
	  }
	  if (options.hasOwnProperty('select')) {
	    book = options.select;
	  }
	  if (typeof book === 'undefined') {
	    book = cits.project.book;
	  }
	  criteria = {
	    'limit': 1000000,
	    '_sort': 'sort_value'
	  };
	  if (options.hasOwnProperty('collection')) {
	    criteria['collection__identifier'] = options.collection;
	  }
	  if (options.hasOwnProperty('language')) {
	    criteria['corpus__language'] = options.language;
	  }
	  //TODO: add in a preselects check
	  api.getItemsFromDatabasePromise('transcriptions', 'work', criteria).then(function(data) {
	    forms.populateSelect(data.results, document.getElementById('biblical_work'), {
	      'value_key': 'id',
	      'text_keys': 'name',
	      'selected': book
	    });
	    if (typeof callback !== 'undefined') {
	      callback();
	    }
	  });
	};

    //TODO: think about losing punctuation for the citation basetexts
    //TODO: is this general enough for the utils file, or shared js?
    stripTags = function(string) {
    	var tag_regex, end_tag_regex, space_tag_regex;
    	space_tag_regex = /<w.*?>/g;
    	end_tag_regex = /<\/.*?>/g;
    	tag_regex = /<[^w/].+?>/g;
    	return string.replace(space_tag_regex, ' ').replace(end_tag_regex, '').replace(tag_regex, '').replace(/\n|\r|\t/g, ' ');
    };

    //this could be changed to use the new 'verse_reading' model if we keep that
    //and also use it for the basetexts. This is fine for now.
    getBiblicalText = function (json) {
    	var book, chapter, verse, language, text, siglum, label, criteria;
    	if (typeof json === 'undefined') {
    		//get the data from the html form
    		book = document.getElementById('biblical_work').value;
    		chapter = document.getElementById('chapter').value;
    		verse = document.getElementById('verse').value;
    		language = document.getElementById('language').value;
    	} else {
    		book = json.biblical_work;
    		chapter = json.chapter;
    		verse = json.verse;
    		language = json.language;
    	}
    	//only carry on if we have all of the info we need
    	if (book !== 'none' && book !== undefined
    		&& chapter !== '' && chapter !== undefined
    			&& verse !== '' && verse !== undefined
    				&& language !== 'none' && language !== undefined) {
    		//check project info
    		if (cits.project.hasOwnProperty('base_text_siglum')) {
    			siglum = cits.project.base_text_siglum;
    			if (cits.project.hasOwnProperty('base_text_label')) {
    				label = cits.project.base_text_label;
    			} else {
    				label = cits.project.base_text_siglum;
    			}
    		} else {
    			if (language === 'grc') {
    				siglum = 'TR';
    				label = 'TR';
    			}
    			if (language === 'lat') {
    				siglum = 'vg^st5';
    				label = 'Vulgate';
    			}
    		}
    		criteria = {'siglum': siglum,
    					'transcription__corpus__identifier': 'NT_' + language.toUpperCase(),
    					'work__id': book,
    					'chapter_number': chapter,
    					'verse_number': verse,
    					'language': language,
    					'_fields': 'tei,id,identifier'};
    		api.getItemsFromDatabasePromise('transcriptions', 'verse', criteria).then(function (verse_data) {
    			if (verse_data.count === 1) {
    				document.getElementById('basetext_label').innerHTML = label + ' text:';
        			text = verse_data.results[0].tei;
        			document.getElementById('basetext_text').innerHTML = stripTags(text);
        			//TODO: ? For comcitation we also used this text in lemma_text, exegesis_text and lemma_text_reminder
    			} else {
    				document.getElementById('basetext_label').innerHTML = '';
    				document.getElementById('basetext_text').innerHTML = '';
    				//TODO: decide whether transcribers are permitted to continue without a base text or not.
    			}
    		});//, 'GET', function (verse_data) {
    		// 	if (verse_data.count === 1) {
    		// 		document.getElementById('basetext_label').innerHTML = label + ' text:';
        // 			text = verse_data.results[0].tei;
        // 			document.getElementById('basetext_text').innerHTML = stripTags(text);
        // 			//TODO: ? For comcitation we also used this text in lemma_text, exegesis_text and lemma_text_reminder
    		// 	} else {
    		// 		document.getElementById('basetext_label').innerHTML = '';
    		// 		document.getElementById('basetext_text').innerHTML = '';
    		// 		//TODO: decide whether transcribers are permitted to continue without a base text or not.
    		// 	}
    		// });
    	}
    };

		displayClavis = function() {
		  if (document.getElementById('work').value !== 'none') {
		    api.getItemFromDatabasePromise('citations', 'work', document.getElementById('work').value).then(function(data) {
		      if (data.hasOwnProperty('clavis') && data.clavis !== '') {
		        document.getElementById('clavis_check').innerHTML = 'Clavis: ' + data.clavis;
		      } else {
		        document.getElementById('clavis_check').innerHTML = 'No clavis';
		      }
		    }).catch(function() {
		      document.getElementById('clavis_check').innerHTML = ''
		    });
		  } else {
		    document.getElementById('clavis_check').innerHTML = '';
		  }
		};

    doShowEditionDetails = function (edition) {
    	var editor, date, title, series, volume, superseded;
    	if (edition.hasOwnProperty('editor') && edition.editor !== '') {
			editor = edition.editor + ' ';
		} else {
			editor = '';
		}
		if (edition.hasOwnProperty('year') && edition.year !== null) {
			date = '(' + edition.year + ') ';
		} else {
			date = '';
		}
		if (edition.hasOwnProperty('independent_title') && edition.independent_title !== '') {
			title = '<i>' + edition.independent_title + '.</i> ';
		} else {
			title = '';
		}
		if (edition.hasOwnProperty('series') && edition.series !== null ) {
			series = edition.series + ' ';
		} else {
			series = '';
		}
		if (edition.hasOwnProperty('volume') && edition.volume !== '') {
			volume = edition.volume + '.';
		} else {
			volume = '.';
		}
		if (edition.hasOwnProperty('superseded') && edition.superseded === true) {
			superseded = ' (superseded)';
		} else {
			superseded = '';
		}
		document.getElementById('edition_details').innerHTML = editor + date + title + series + volume + superseded;
    };

    showEditionDetails = function (edition_id) {
    	if (typeof edition_id === 'undefined') {
    		edition_id = document.getElementById('edition').value;
    	}
    	if (edition_id !== 'none' && edition_id !== '' && edition_id !== null) {
    		api.getItemFromDatabasePromise('citations', 'edition', edition_id).then(function (edition) {
    			doShowEditionDetails(edition);
    		});
    	} else {
    		document.getElementById('edition_details').innerHTML = '';
    	}
    };

    populateEditionSelect = function(citation_json) {
  var criteria, edition;
  if (citation_json === undefined) {
    citation_json = {};
  }
  criteria = {
    'limit': 1000000,
    'work__language': cits.project.language,
    '_sort': 'id'
  };
  if (citation_json.hasOwnProperty('work') && citation_json.work !== null) {
    criteria.work__id = citation_json.work;
  }
  if (citation_json.hasOwnProperty('author') && citation_json.author !== null) {
    criteria.author__id = citation_json.author;
  } else if (cits.project.hasOwnProperty('author_ids')) {
    if (cits.project.author_ids.length === 1) {
      criteria.author__id = cits.project.author_ids[0];
    }
  }
  if (citation_json.hasOwnProperty('edition') && citation_json.edition !== null) {
    edition = citation_json.edition;
  } else {
    edition = 'none';
  }
  api.getItemsFromDatabasePromise('citations', 'edition', criteria).then(function(edition_data) {
    forms.populateSelect(edition_data.results,
      document.getElementById('edition'), {
        'value_key': 'id',
        'text_keys': {
          '1': 'editor',
          '2': 'series',
          '3': 'year',
          '4': 'legacy_edition'
        },
        'selected': edition
      });
    if (edition !== 'none') {
      showEditionDetails(edition);
    }
  });
};

	addEventHandlers = function(model) {
	  var i, idList;
	  edit.addEventHandlers(model);
	  idList = ['biblical_work', 'chapter', 'verse', 'language'];
	  for (i = 0; i < idList.length; i += 1) {
	    $('#' + idList[i]).on('change', function() {
	      getBiblicalText();
	    });
	  }
		idList = ['biblical_work', 'chapter', 'verse'];
	  for (i = 0; i < idList.length; i += 1) {
	    $('#' + idList[i]).on('change', function() {
	      setBiblicalReferenceFields();
	    });
	  }
	  $('#author').on('change', function(event) {
	    edit.filterData('citation', event.target.id, event.target.value, false, displayExtras);
	    forms.showValidateElement(document.getElementById('author'));
	  });
	  $('#work').on('change', function(event) {
	    edit.filterData('citation', event.target.id, event.target.value, false, displayExtras);
	    forms.showValidateElement(document.getElementById('work'));
	    displayClavis();
	  });
	  $('#edition').on('change', function(event) {
	    showEditionDetails(document.getElementById('edition').value);
	  });
	  $('#delete_corrections_required_data').on('click', function(event) {
	    var ok;
	    ok = confirm('This will delete all of the correction notes.\nAre you sure all of the required corrections have been made and the notes can be deleted?');
	    if (ok) {
	      document.getElementById('corrections_required').value = '';
	      document.getElementById('correction_notes').value = '';
	      document.getElementById('corrections_section').style.display = 'none';
	    } else {
	      return;
	    }
	  });
	  $('#delete_manuscript_info').on('click', function(event) {
	    var ok;
	    ok = confirm('Are you sure you want to delete the manuscript information?\nThis should only be done if all of the data has been incorporated into the manuscript variants boxes above.');
	    if (ok) {
	      document.getElementById('manuscript_info').value = '';
	      document.getElementById('manuscript_info').style.display = 'none';
	      document.getElementById('manuscript_info_div').style.display = 'none';
	    } else {
	      return;
	    }
	  });
	  $('#add_manuscript_variants').on('click', function(event) {
	    addManuscriptVariants();
	  });
	  $('#delete_dependencies_string').on('click', function(event) {
	    var ok;
	    ok = confirm('Are you sure you want to delete this dependency information?\nThis should only be done if all of the data has been incorporated into the dependency boxes above.');
	    if (ok) {
	      document.getElementById('dependencies_string').value = '';
	      document.getElementById('dependencies_string').style.display = 'none';
	      document.getElementById('dependencies_string_div').style.display = 'none';
	    } else {
	      return;
	    }
	  });
	  $('#add_dependencies').on('click', function(event) {
	    addDependency();
	  });
	  $('#add_parallel').on('click', function(event) {
	    addParallel();
	  });
	  $('#add_catena').on('click', function(event) {
	    addCatena();
	  });
	  $('#add_source').on('click', function(event) {
	    addSource();
	  });
	  //TODO: need to make sure buttons are set correctly for current status
	  $('#flag').on('click', function(event) {
	    if (document.getElementById('flag').value === 'Unflag') {
	      document.getElementById('status').value = document.getElementById('status').value.replace(' but flagged', '');
	      document.getElementById('status_value').innerHTML = document.getElementById('status_value').innerHTML.replace(' but flagged', '');
	      document.getElementById('flag').value = 'Flag for attention';
	    } else {
	      document.getElementById('status').value = document.getElementById('status').value + ' but flagged';
	      document.getElementById('status_value').innerHTML = document.getElementById('status_value').innerHTML + ' but flagged';
	      document.getElementById('flag').value = 'Unflag';
	    }
	  });
	  $('#deprecate').on('click', function(event) {
	    if (document.getElementById('deprecate').value === 'Deprecate') {
	      document.getElementById('status').value = 'deprecated';
	      document.getElementById('status_value').innerHTML = 'Deprecated';
	      document.getElementById('deprecate').value = 'Make live';
	      document.getElementById('flag').value = 'Flag for attention';
	    } else {
	      document.getElementById('status').value = 'live';
	      document.getElementById('status_value').innerHTML = 'Live';
	      document.getElementById('deprecate').value = 'Deprecate';
	      document.getElementById('flag').value = 'Flag for attention';
	    }
	  });
	  //submit options specific to citations
	  $('#submit_same').on('click', function() {
	    var bibref;
	    bibref = getVerseReference();
	    submit.submit(model, model + '_form', true, function(data, reload) {
				if (window.location.pathname.substr(-1) === '/') {
					window.location = '/citations/citation/edit/' + window.location.search + '#' + $.param(bibref)
				} else {
					window.location = '/citations/citation/edit' + window.location.search + '#' + $.param(bibref)
				}
				if (reload === true) {
					window.location.reload();
					window.scrollTo(0, 0);
				}
			});
	  });
	  $('#submit_next').on('click', function() {
      var bibref, callback;
      callback = function(bibref) {
        submit.submit(model, model + '_form', true, function(data, reload) {
          if (window.location.pathname.substr(-1) === '/') {
            window.location.href = '/citations/citation/edit/' + window.location.search + '#' + $.param(bibref);
          } else {
            window.location.href = '/citations/citation/edit' + window.location.search + '#' + $.param(bibref);
          }
          if (reload == true) {
            window.location.reload(true);
            window.scrollTo(0, 0);
          }
        })
      };
	    bibref = getVerseReference();
	    getNextVerse(bibref, callback);
	  });
	};

	getVerseReference = function () {
		var reference, chapter, verse;
		reference = {};
		reference.language = document.getElementById('language').value;
		reference.biblical_work = document.getElementById('biblical_work').value;
		chapter = document.getElementById('chapter').value;
		if (!isNaN(parseInt(chapter))) {
			reference.chapter = parseInt(chapter);
		} else {
			reference.chapter = chapter;
		}
		verse = document.getElementById('verse').value;
		if (!isNaN(parseInt(verse))) {
			reference.verse = parseInt(verse);
		} else {
			reference.verse = verse;
		}
    	return reference;
    };

    getNextVerse = function (bibref, callback) {
			var criteria;
    	if (bibref.biblical_work === 'none' && !Number.isInteger(bibref.verse), !Number.isInteger(bibref.chapter)) {
    		callback(bibref);
    		return;
    	}
    	if (Number.isInteger(bibref.verse) && (bibref.biblical_work === 'none' || !Number.isInteger(bibref.chapter))) {
    		bibref.verse = bibref.verse + 1;
    		callback(bibref);
    		return;
    	}
    	if (bibref.chapter === 0 && bibref.verse === 0) {
    		bibref.chapter = 1;
    		bibref.verse = 1;
    		callback(bibref);
    		return;
    	}
			criteria = {'work__id': bibref.biblical_work, 'corpus__identifier': 'NT_' + bibref.language.toUpperCase()};
    	api.getItemsFromDatabasePromise('transcriptions', 'structure', criteria).then(function(structure) {
				if (structure.count === 1) {
					if (bibref.verse < structure.results[0].verses_per_chapter[bibref.chapter]) {
	    			bibref.verse = bibref.verse + 1;
	    		} else if (bibref.chapter < structure.results[0].total_chapters) {
	    			bibref.chapter = bibref.chapter + 1;
	    			bibref.verse = 1;
	    		}
	    		callback(bibref);
				} else {
					//just try adding a verse and hope for the best
					bibref.verse = bibref.verse + 1;
	            callback(bibref);
				}
    	}).catch(function () {
    		bibref.verse = bibref.verse + 1;
            callback(bibref);
    	});
    	return;
    };

	//used for filtering dependency works only
	filterWorks = function (seed_id, target_id) {
		var seed, work, criteria;
		seed = document.getElementById(seed_id).value;
		criteria = {'limit': 1000000, 'author__id': seed, '_sort': 'abbreviation', '_fields': 'abbreviation,title,id'};
		api.getItemsFromDatabasePromise('citations', 'work', criteria).then(function (works) {
			works = works.results;
			if (works.length === 1) {
				work = works[0].id;
			}
			forms.populateSelect(works, document.getElementById(target_id), {'value_key': 'id',
																			'text_keys': {1: 'abbreviation', 2: 'title'},
																			'selected': work,
																			'add_class': {'data_key': 'obsolete', 'data_value': true, 'class_name': 'obsolete'}});
		});
	};

	populateDependencyAuthor = function (index, data) {
		var selected, settings, criteria;
		if (typeof data !== 'undefined' && data.hasOwnProperty('author') && data.author !== null) {
			selected = data.author;
		}
		criteria = {'limit': 1000000, '_sort': 'abbreviation', '_fields': 'abbreviation,full_name,id'};
		api.getItemsFromDatabasePromise('citations', 'author', criteria).then(function (authors) {
			settings = {'value_key': 'id',
					'text_keys': {1 : 'abbreviation', 2 : 'full_name'},
					'selected': selected,
					'add_class': {'data_key': 'obsolete', 'data_value': true, 'class_name': 'obsolete'}}
			forms.populateSelect(authors.results, document.getElementById('dependencies_' + index + '_author'), settings);

			$('#dependencies_' + index + '_author').on('change', function () {
				filterWorks('dependencies_' + index + '_author', 'dependencies_' + index + '_work');
			});
		});
	};

	populateDependencyWork = function (index, data) {
		var work, settings, criteria;
		criteria = {'limit': 1000000, '_sort': 'abbreviation', '_fields': 'abbreviation,title,id'};
		api.getItemsFromDatabasePromise('citations', 'work', criteria).then(function (works) {
			if (typeof data !== 'undefined' && data.hasOwnProperty('work') && data.work !== null) {
				work = data.work;
			}
			settings = {'value_key': 'id',
					'text_keys': {1: 'abbreviation', 2: 'title'},
					'selected': work,
					'add_class': {'data_key': 'obsolete', 'data_value': true, 'class_name': 'obsolete'}}
			forms.populateSelect(works.results, document.getElementById('dependencies_' + index + '_work'), settings);
		});
	};

	addCatena = function (reference) {
		var parent, row, table;
		if (typeof reference === 'undefined') {
			if (document.getElementById('book_catena').value !== 'none'
					&& document.getElementById('chapter_catena').value !== ''
					&& document.getElementById('verse_catena').value !== '') {
				reference = document.getElementById('book_catena').value + ' '
					+ document.getElementById('chapter_catena').value + ':'
					+ document.getElementById('verse_catena').value;
				document.getElementById('book_catena').value = 'none';
				document.getElementById('chapter_catena').value = '';
				document.getElementById('verse_catena').value = '';
			}
		}
		//check again to see if we have managed to set it with data from the form
		if (typeof reference !== 'undefined') {
			table = document.getElementById('catena_table');
			table.style.display = 'inline-block';
			parent = table.getElementsByTagName('tbody')[0];
			row = document.createElement('tr');
			row.innerHTML = '<td class="rowhandler"><div class="drag row"></div></td><td id="biblical_catena_'
				+ catenaCount + '">'
				+ reference
				+ '</td><td><img class="delete_logo" height="15px" width="15px" id="delete_catena_'
				+ catenaCount
				+ '" title="Delete this catena" src="' + staticUrl + '/citations/images/delete.png"/></td>';
			parent.appendChild(row);
			$('#delete_catena_' + catenaCount).on('click', function (event) {
				if (event.target.parentNode.parentNode.parentNode.getElementsByTagName('TR').length === 1) {
					event.target.parentNode.parentNode.parentNode.parentNode.style.display = 'none';
				}
				deleteElement(event.target.parentNode.parentNode);
			});
			redipsInit('drag2');
			catenaCount += 1;
		} else {
			return;
		}
	};

	addParallel = function (reference) {
		var parent, row, table;
		if (typeof reference === 'undefined') {
			if (document.getElementById('book_parallel').value !== 'none'
						&& document.getElementById('chapter_parallel').value !== ''
							&& document.getElementById('verse_parallel').value !== '') {
				reference = document.getElementById('book_parallel').value + ' '
							+ document.getElementById('chapter_parallel').value + ':'
								+ document.getElementById('verse_parallel').value;
				//reset the form elements
				document.getElementById('book_parallel').value = 'none';
				document.getElementById('chapter_parallel').value = '';
				document.getElementById('verse_parallel').value = '';
			}
		}
		//check again to see if we have managed to set it with data from the form
		if (typeof reference !== 'undefined') {
			table = document.getElementById('parallels_table');
			table.style.display = 'inline-block';
			parent = table.getElementsByTagName('tbody')[0];
			row = document.createElement('tr');
			row.innerHTML = '<td id="biblical_parallels_' + parallelCount
				+ '">' + reference
				+ '</td><td><img class="delete_logo" height="15px" width="15px" id="delete_parallel_'
				+ parallelCount
				+ '" title="Delete this parallel" src="' + staticUrl + '/citations/images/delete.png"/></td>';
			parent.appendChild(row);

			$('#delete_parallel_' + parallelCount).on('click', function (event) {
				if (event.target.parentNode.parentNode.parentNode.getElementsByTagName('TR').length === 1) {
					event.target.parentNode.parentNode.parentNode.parentNode.style.display = 'none';
				}
				deleteElement(event.target.parentNode.parentNode);
			});
			parallelCount += 1;
		} else {
			return;
		}
	};

	addSource = function (source) {
		if (source === undefined) {
			if (document.getElementById('source_select').value !== '') {
				source = document.getElementById('source_select').value;
				//reset the form element
				document.getElementById('source_select').value = '';
			}
		}
		if (source !== undefined) {
			table = document.getElementById('sources_table');
			table.style.display = 'inline-block';
			parent = table.getElementsByTagName('tbody')[0];
			row = document.createElement('tr');
			if (cits.user.group_name === 'citation_managers') {
				row.innerHTML = '<td id="sources_' + sourceCount
				+ '">' + source + '</td>'
				+ '<td><img class="delete_logo" height="15px" width="15px" id="delete_source_'
				+ sourceCount
				+ '" title="Delete this source" src="' + staticUrl + '/citations/images/delete.png"/></td>';
			} else {
				row.innerHTML = '<td id="sources_' + sourceCount
				+ '">' + source + '</td>'
				+ '<td></td>';
			}
			parent.appendChild(row);

			$('#delete_source_' + sourceCount).on('click', function (event) {
				if (event.target.parentNode.parentNode.parentNode.getElementsByTagName('TR').length === 1) {
					event.target.parentNode.parentNode.parentNode.parentNode.style.display = 'none';
				}
				deleteElement(event.target.parentNode.parentNode);
			});
			sourceCount += 1;
		} else {
			return;
		}
	};

	addDependency = function (data) {
		var parent, newDiv, html;
		parent = document.getElementById('dependencies_data_div');
		newDiv = document.createElement('fieldset');
		newDiv.setAttribute('class', 'data_group objectlist');
		newDiv.setAttribute('id', 'dependencies_' + dependencyCount);
		html = [];
		html.push('<label class="inline">relationship:<select id="dependencies_');
		html.push(dependencyCount + '_relation_type" name="dependencies_');
        html.push(dependencyCount + '_relation_type" class="string"><option value="">select</option><option value="is_quoted_in">is quoted in</option><option value="is_same_as">is same as</option><option value="is_quotation_of">is quotation of</option><option value="is_derived_from">is derived from</option><option value="see_also">see also</option><option value="formerly_known_as">formerly known as</option></select></label>');
        html.push('<label class="inline inner">author:<select id="dependencies_');
        html.push(dependencyCount + '_author" name="dependencies_');
        html.push(dependencyCount + '_author" class="integer"></select></label>');
        html.push('<label class="inline inner">work:<select id="dependencies_');
        html.push(dependencyCount + '_work" name="dependencies_');
        html.push(dependencyCount + '_work" class="integer"></select></label>');
        html.push('<label class="inline inner">work reference:<input type="text" id="dependencies_');
        html.push(dependencyCount + '_work_reference" name="dependencies_');
        html.push(dependencyCount + '_work_reference" class="string"/></label>');
        html.push('<img class="delete_logo" height="20px" width="20px" id="delete_dependency_');
        html.push(dependencyCount + '" title="Delete this dependency" src="' + staticUrl + 'citations/images/delete.png"/>');
        newDiv.innerHTML = html.join('');
        parent.appendChild(newDiv);
        populateDependencyAuthor(dependencyCount, data);
        populateDependencyWork(dependencyCount, data);
        $('#delete_dependency_' + dependencyCount).on('click', function (event) {
        	utils.deleteElement(event.target.parentNode);
        });
        dependencyCount += 1;
    };

    getLanguage = function () {
    	if (cits.project.hasOwnProperty('language')) {
    		return cits.project.language;
    	}
    	if (document.getElementById('language') && document.getElementById('language').value !== 'none') {
    		return document.getElementById('language').value;
    	}
    	return null;
    };

    addManuscriptVariants = function () {
    	/*add a new line of manuscript variant boxes to fill in */
    	var html, table, newDiv, newRow, newCell, idList, i, language;
    	language = getLanguage();
    	if (language === null) {
    		alert('You must select a language before continuing');
    		return;
    	}

    	table = document.getElementById('MS_variants');
    	newRow = document.createElement('tr');
    	newCell = document.createElement('td');
    	newCell.setAttribute('class', 'rowhandler');
    	newCell.innerHTML = '<div class="drag row"></div>';
    	newRow.appendChild(newCell);
    	newCell = document.createElement('td');
    	newDiv = document.createElement('fieldset');
    	newDiv.setAttribute('class', 'data_group objectlist');
    	newDiv.setAttribute('id', 'manuscript_variants_' + msVariantCount);

    	html = [];
    	idList = [];
    	html.push('<label class="inline">headword:<input size="20" class="string" type="text" name="manuscript_variants_');
    	html.push(msVariantCount + '_headword" id="manuscript_variants_');
    	html.push(msVariantCount + '_headword"/></label>');
    	idList.push('manuscript_variants_' + msVariantCount + '_headword');
    	html.push('<label class="inline inner">variant:<input size="20" class="string" type="text" name="manuscript_variants_');
    	html.push(msVariantCount + '_variant" id="manuscript_variants_');
    	html.push(msVariantCount + '_variant"/></label>');
    	idList.push('manuscript_variants_' + msVariantCount + '_variant');
    	html.push('<label class="inline inner">MS support:<input size="15" class="string" type="text" name="manuscript_variants_');
    	html.push(msVariantCount + '_support" id="manuscript_variants_');
    	html.push(msVariantCount + '_support"/></label>');
    	idList.push('manuscript_variants_' + msVariantCount + '_support');
    	if (language === 'lat') {
    		html.push('<label class="inline inner">vulgate?<input class="boolean" type="checkbox" name="manuscript_variants_');
    		html.push(msVariantCount + '_vulgate" id="manuscript_variants_');
    		html.push(msVariantCount + '_vulgate"/></label>');
    		idList.push('manuscript_variants_' + msVariantCount + '_vulgate');
    	}
    	if (language === 'grc') {
    		html.push('<label class="inline inner">maj?<input class="boolean" type="checkbox" name="manuscript_variants_');
    		html.push(msVariantCount + '_maj" id="manuscript_variants_');
    		html.push(msVariantCount + '_maj"/></label>');
    		idList.push('manuscript_variants_' + msVariantCount + '_maj');
    	}
    	html.push('<img class="delete_logo" height="20px" width="20px" id="delete_manuscript_variants_');
    	html.push(msVariantCount + '" title="Delete this variant" src="' + staticUrl + '/citations/images/delete.png"/>');
    	newDiv.innerHTML = html.join('');

    	newCell.appendChild(newDiv);
    	newRow.appendChild(newCell);
    	table.childNodes[0].appendChild(newRow);
    	$('#delete_manuscript_variants_' + msVariantCount).on('click', function (event) {
    		deleteElement(event.target.parentNode.parentNode.parentNode);
    	});

    	for (i = 0; i < idList.length; i += 1) {
    		$('#' + idList[i]).on('change', function (event) {
    			forms.validateElement(event.target);
    		});
    	}
    	redipsInit('drag1');
    	msVariantCount += 1;
    };

    displayExtras = function () {
    	displayClavis();
    	showEditionDetails();
  	};

  	createBiblicalReference = function (json, callback) {
			var book, chapter, verse;
			api.getItemFromDatabase('transcriptions', 'work', json.biblical_work, function (response){
				sort_ref = 0
				biblical_ref = response.abbreviation + '.' + json.chapter + '.' + json.verse
				callback(biblical_ref);
			});
  	};

    //----------------END PRIVATE METHODS----------------

	//----------------BEGIN PUBLIC METHODS----------------

    redipsInit = function (id) {
        // reference to the REDIPS.drag library and message line
        var rd = REDIPS.drag;
        rd.init(id);
    };

    customSerialiseForm = function (form_id) {
    	var json, catena, parallels, sources, rows;
    	json = forms.serialiseForm(form_id);
			//createBiblicalReference(json, function (response){
				// console.log('now in then')
				// json.biblical_reference = response;
				// console.log(json.biblical_reference)
				// json.biblical_reference = 'test'
				// json.biblical_reference_sortable = 0
	    	catena = [];
	    	$('#' + form_id + ' #catena_table > tbody > tr').each(function () {
	    		catena.push($(this).find('td').eq(1).text());
	    	});
	    	if (catena.length > 0) {
	    		json.biblical_catena = catena;
	    	} else {
	    		json.biblical_catena = null;
	    	}
	    	parallels = [];
	    	$('#' + form_id + ' #parallels_table > tbody > tr').each(function () {
	    		parallels.push($(this).find('td').eq(0).text());
	    	});
	    	if (parallels.length > 0) {
	    		json.biblical_parallels = parallels;
	    	} else {
	    		json.biblical_parallels = null;
	    	}
	    	sources = [];
	    	$('#' + form_id + ' #sources_table > tbody > tr').each(function () {
	    		sources.push($(this).find('td').eq(0).text());
	    	});
	    	if (sources.length > 0) {
	    		json.sources = sources;
	    	} else {
	    		json.sources = null;
	    	}
				console.log(json)
	    	return json;
			//});
    };

    //TODO: add in special preselects for citation based on transcriber type
	loadData = function (model, data) {

		var language, book, author, work, edition, onlinecorpus, i, date, to_disable, options, criteria;
		book = data.biblical_work;
		work = data.work;
		edition = data.edition || 'none';
		onlinecorpus = data.onlinecorpus || 'none';
		if (data.hasOwnProperty('language')) {
			language = data.language;
		} else {
			language = cits.project.language;
		}
		options = {'select': book, 'collection': 'NT'};
		populateBook(options, function () {
			if (!cits.user.hasOwnProperty('group_name')
					|| cits.user.group_name !== "citation_managers") {
				forms.disableFields(['biblical_work'], model + '_form');
			}
		});
		api.getItemFromDatabasePromise('citations', 'work', work).then(function (work_json){
			author = work_json.author || 'none';
			edit.populateAuthor(model, {'select': author, 'inc_obsolete': false}, function () {
				if (!cits.user.hasOwnProperty('group_name')
						|| cits.user.group_name !== "citation_managers") {
					forms.disableFields(['author'], model + '_form');
				}
			});
		});
		edit.populateWork(model, {'select': work, 'inc_obsolete': false, 'author': author}, function () {
			if (!cits.user.hasOwnProperty('group_name')
					|| cits.user.group_name !== "citation_managers") {
				forms.disableFields(['work'], model + '_form');
			}
			displayClavis();
		});

		populateEditionSelect(data);
		edit.populateOnlinecorpus(model, {'select': onlinecorpus}, function () {
			if (!cits.user.hasOwnProperty('group_name')
					|| cits.user.group_name !== "citation_managers") {
				forms.disableFields(['onlinecorpus'], model + '_form');
			}
		});
		//populate specific form fields for references
		criteria = {'limit': 1000000, '_sort': 'collection__identifier,sort_value', '_fields': 'id,sort_value,name,collection'};
		api.getItemsFromDatabasePromise('transcriptions', 'work', criteria).then(function (book_data) {
			forms.populateSelect(book_data.results, document.getElementById('book_catena'), {'value_key': 'name', 'text_keys': 'name'});
			forms.populateSelect(book_data.results, document.getElementById('book_parallel'), {'value_key': 'name', 'text_keys': 'name'});
		});
		getBiblicalText(data);
		setBiblicalReferenceFields({'biblical_work': data.biblical_work, 'chapter': data.chapter, 'verse': data.verse});
		//show legacy data fields if required
		if (data.hasOwnProperty('manuscript_info') && data.manuscript_info !== '') {
			document.getElementById('manuscript_info_div').style.display = 'block';
			if (cits.user.group_name === "citation_managers") {
				document.getElementById('delete_manuscript_info').style.display = 'inline-block';
			}
		}
		if (data.hasOwnProperty('dependencies_string') && data.dependencies_string !== '') {
			document.getElementById('dependencies_string_div').style.display = 'block';
			if (cits.user.group_name === "citation_managers") {
				document.getElementById('delete_dependencies_string').style.display = 'inline-block';
			}
		}
		//manually populate the non-form fields data
		if (data.hasOwnProperty('biblical_catena') && data.biblical_catena !== null) {
			for (i = 0; i < data.biblical_catena.length; i += 1) {
				addCatena(data.biblical_catena[i]);
			}
		}
		if (data.hasOwnProperty('biblical_parallels') && data.biblical_parallels !== null) {
			for (i = 0; i < data.biblical_parallels.length; i += 1) {
				addParallel(data.biblical_parallels[i]);
			}
		}
		//now combine the two potential sources lists and add the result (sources in the citation data first)
		//if there are none in the data add the project ones anyway if there are some
		if (data.hasOwnProperty('sources') && data.sources !== null) {
			if (cits.project.hasOwnProperty('sources') && cits.project.sources !== null) {
				for (i = 0; i < cits.project.sources.length; i += 1) {
					if (data.sources.indexOf(cits.project.sources[i]) === -1) {
						data.sources.push(cits.project.sources[i]);
					}
				}
			}
			document.getElementById('source_section').style.display = 'block';
			for (i = 0; i < data.sources.length; i += 1) {
				addSource(data.sources[i]);
			}
		} else if (cits.project.hasOwnProperty('sources') && cits.project.sources !== null) {
			document.getElementById('source_section').style.display = 'block';
			for (i = 0; i < cits.project.sources.length; i += 1) {
				addSource(cits.project.sources[i]);
			}
		}
		if (cits.user.hasOwnProperty('group_name') && cits.user.group_name === 'citation_managers') {
			document.getElementById('new_source_div').style.display = 'block';
		}
		if (data.hasOwnProperty('status') && data.status !== '') {
			document.getElementById('status').value = data.status;
			document.getElementById('status_value').innerHTML = data.status.charAt(0).toUpperCase() + data.status.slice(1);
			if (data.status.indexOf('deprecated') !== -1) {
				document.getElementById('deprecate').value = 'Make live';
			}
			if (data.status.indexOf('but flagged') !== -1) {
            	document.getElementById('flag').value = 'Unflag';
			} else {
            	document.getElementById('flag').value = 'Flag for attention';
			}
		}
		if (data.hasOwnProperty('corrections_required') && data.corrections_required !== null && cits.user.group_name === 'citation_managers') {
			document.getElementById('corrections_section').style.display = 'block';
		}
		//populate the rest of the form
		if (data.hasOwnProperty('created_time') && data.created_time !== null) {
			date = new Date(data.created_time);
			document.getElementById('created_time_display').value = date.getDate() + '/' + (date.getMonth() + 1) + '/' + date.getFullYear();
		}
		if (data.hasOwnProperty('last_modified_time') && data.last_modified_time !== null) {
			date = new Date(data.last_modified_time);
			document.getElementById('last_modified_time_display').value = date.getDate() + '/' + (date.getMonth() + 1) + '/' + date.getFullYear();
			document.getElementById('modifier_details').style.display = 'inline';
		}
		//make sure we have at the right amount of boxes visible for dynamic fields
		if (data.manuscript_variants !== null && data.manuscript_variants.length > 0) {
			for (i = 0; i < data.manuscript_variants.length; i += 1) {
				addManuscriptVariants(data.manuscript_variants[i]);
			}
		} else {
			addManuscriptVariants();
		}
		if (data.dependencies !== null && data.dependencies.length > 0) {
			for (i = 0; i < data.dependencies.length; i += 1) {
				addDependency(data.dependencies[i]);
			}
		} else {
			addDependency();
		}
		if (cits.user.hasOwnProperty('group_name')
				&& cits.user.group_name === "citation_managers") {
			to_disable = []
		} else {
			to_disable = ['chapter', 'verse']
		}
		edit.loadData(model, data, to_disable);
		addEventHandlers(model);
	};

	setBiblicalReferenceFields = function (data) {
		var biblical_reference_sortable;
		if (data === undefined) {
			data = {};
			if (document.getElementById('biblical_work').value !== '') {
				data.biblical_work = parseInt(document.getElementById('biblical_work').value);
			}
			if (document.getElementById('chapter').value !== '') {
				data.chapter = parseInt(document.getElementById('chapter').value);
			}
			if (document.getElementById('verse').value !== '') {
				data.verse = parseInt(document.getElementById('verse').value);
			}
		}
		if (data.hasOwnProperty('biblical_work') && !isNaN(data.biblical_work)
					&& data.hasOwnProperty('chapter') && !isNaN(data.chapter)
					&& data.hasOwnProperty('verse') && !isNaN(data.verse)) {
						api.getItemFromDatabasePromise('transcriptions', 'work',data.biblical_work).then(function (work) {
							document.getElementById('biblical_reference').value = work.abbreviation + '.' + data.chapter + '.' + data.verse;
							biblical_reference_sortable = (work.sort_value*1000000) + (data.chapter*1000) + data.verse;
							document.getElementById('biblical_reference_sortable').value = biblical_reference_sortable;
						});
		} else {
			console.log('problem creating biblical reference');
		}
	};


	prepareForm = function (model, data) {
		var language, selected_book, verse_data, book_criteria, user_status, onlinecorpus_preselect, i, criteria;
		user_status = edit.getUserStatus();
		if (window.location.hash.substr(1) !== '') {
			verse_data = utils.getObjectFromQueryString(window.location.hash.substr(1));
			document.getElementById('chapter').value = verse_data.chapter;
			document.getElementById('verse').value = verse_data.verse;
			selected_book = parseInt(verse_data.biblical_work);
			setBiblicalReferenceFields({'biblical_work': parseInt(verse_data.biblical_work), 'chapter': verse_data.chapter, 'verse': verse_data.verse});
			document.getElementById('language').value = verse_data.language;
			getBiblicalText(verse_data);
			language = verse_data.language;
		} else {
			if (cits.project.hasOwnProperty('biblical_work')) {
				selected_book = cits.project.biblical_work;
			}
			if (cits.project.hasOwnProperty('language')) {
				language = cits.project.language;
			}
		}
		book_criteria = {'collection': 'NT'};
		if (selected_book !== undefined) {
			book_criteria['select'] = selected_book;
		}
		populateBook(book_criteria, function () {
			if (!cits.user.hasOwnProperty('group_name')
					|| (model !== 'privatecitation' && cits.user.group_name !== "citation_managers")
						|| (model === 'privatecitation' && cits.user.group_name !== "private_citation_managers")) {
				forms.disableFields(['biblical_work'], model + '_form');
			}
		});
		edit.populateAuthor(model, {'inc_obsolete': false});
		//do not populate work and disable the select until we have an author (because selecting the right work is too difficult)
		document.getElementById('work').disabled = true;
		//may as well disable edition as well
		document.getElementById('edition').disabled = true;
		onlinecorpus_preselect = {};
		if (user_status
				&& cits.project.hasOwnProperty('preselects')
				&& cits.project.preselects.hasOwnProperty('citation')
				&& cits.project.preselects.citation.hasOwnProperty(user_status)
				&& cits.project.preselects.citation[user_status].hasOwnProperty('onlinecorpus')) {
			onlinecorpus_preselect = {'select': cits.project.preselects.citation[user_status].onlinecorpus};
		}
		edit.populateOnlinecorpus(model, onlinecorpus_preselect, function () {
			if (!cits.user.hasOwnProperty('group_name')
					|| cits.user.group_name !== "citation_managers") {
				forms.disableFields(['onlinecorpus'], model + '_form');
			}
		});
		populateTranscriber();
		criteria = {'limit': 1000000, '_sort': 'collection__identifier,sort_value', '_fields': 'sort_value,name'};
		api.getItemsFromDatabasePromise('transcriptions', 'work', criteria).then(function (book_data) {
			forms.populateSelect(book_data.results, document.getElementById('book_catena'), {'value_key': 'name', 'text_keys': 'name'});
			forms.populateSelect(book_data.results, document.getElementById('book_parallel'), {'value_key': 'name', 'text_keys': 'name'});
		});
		if (cits.project.hasOwnProperty('sources') && cits.project.sources !== null) {
			document.getElementById('source_section').style.display = 'block';
			for (i = 0; i < cits.project.sources.length; i += 1) {
				addSource(cits.project.sources[i]);
			}
		}
		if (cits.user.group_name === 'citation_managers') {
			document.getElementById('source_section').style.display = 'block';
			document.getElementById('new_source_div').style.display = 'block';
		}
		addManuscriptVariants();
		addDependency();
		edit.prepareForm(model, data);
		addEventHandlers(model);

	};

//
//	//----------------END PUBLIC METHODS----------------
//

	if (testing) {
		return {
			loadData: loadData,
			prepareForm: prepareForm,
			customSerialiseForm: customSerialiseForm,
			populateTranscriber: populateTranscriber,
			populateBook: populateBook,
			stripTags: stripTags,
			getBiblicalText: getBiblicalText,
			addCatena: addCatena,
			addParallel: addParallel,
			addSource: addSource,
			addDependency: addDependency,
			populateDependencyAuthor: populateDependencyAuthor,
			populateDependencyWork: populateDependencyWork,
			addManuscriptVariants: addManuscriptVariants,
			getLanguage: getLanguage,
			filterWorks: filterWorks,
			displayClavis: displayClavis,
			showEditionDetails: showEditionDetails,
			doShowEditionDetails: doShowEditionDetails,
			populateEditionSelect: populateEditionSelect,
			createBiblicalReference: createBiblicalReference,
			getVerseReference: getVerseReference
			};
	} else {
		return {
			loadData: loadData,
			prepareForm: prepareForm,
			customSerialiseForm: customSerialiseForm,
			};
	}

} () );
