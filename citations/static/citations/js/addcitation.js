"use strict";
/*global MAG, document, window */
/*jslint nomen: true*/


//TODO: consider adding language automatically behind the scenes to edition for filtering purposes
//TODO: wild card searching in model list?

var CIT = (function () {
    
    return {

        hello: function () {
            console.log('citations app');
        },

        page_size: 20,
        model_namespace: 'cit_',
        spinner: null,
        _project: {},
        
        idify_string: function (string) {
            string = MAG.TEMPLATE.trim(string);
            string = string.replace(/\?/g, '');
            string = string.replace(/\./g, '');
            string = string.replace(/ /g, '-');
            string = string.replace(/=/, '');
            string = string.replace(/#/g, '');
            string = string.replace(/%/g, '');
            string = string.replace(/\*/g, '');
            string = string.replace(/{/g, '');
            string = string.replace(/}/g, '');
            string = string.replace(/\(/g, '');
            string = string.replace(/\)/g, '');
            string = string.replace(/\\/g, '');
            string = string.replace(/:/g, '');
            string = string.replace(/</g, '');
            string = string.replace(/>/g, '');
            string = string.replace(/\//g, '');
            string = string.replace(/\+/g, '');
            string = string.replace(/&/g, '');
            string = string.replace(/,/g, '');
            return string;
        },
        
        CIT: (function () {
            return {
        	
        	msvariant_count: 0,
        	dependency_count: 0,
        	parallel_count: 0,
        	catena_count: 0,
        	
        	prepare_edition_entry: function (json) {
        		var parent, html, criteria, selected, i, j, populate, edition;
        		if ((typeof json === 'undefined' && CIT._project.hasOwnProperty('edition_lookup')) 
        				|| typeof json !== 'undefined' && json.hasOwnProperty('edition_lookup') 
        				&& CIT._project.hasOwnProperty('edition_lookup')) {
        			document.getElementById('edition_id').disabled = 'disabled';
        			parent = document.getElementById('edition_lookup_div');
        			populate = [];
        			html = [];
        			html.push('<fieldset id="edition_lookup" class="data_group">');
        			for (i = 0; i < CIT._project.edition_lookup.length; i += 1) {
        				if (CIT._project.edition_lookup[i].hasOwnProperty('collection')) {
        					populate.push(CIT._project.edition_lookup[i]);
        					html.push('<label for="edition_lookup_' + CIT._project.edition_lookup[i].id 
        							+ '" class="top width_quarter">' + CIT._project.edition_lookup[i].label
        							+ ':<select name="edition_lookup_' 
        							+ CIT._project.edition_lookup[i].id + '" id="edition_lookup_' 
        							+ CIT._project.edition_lookup[i].id + '"></select></label>');
        				} else {
        					html.push('<label for="edition_lookup_' + CIT._project.edition_lookup[i].id 
        							+ '" class="top width_quarter">' + CIT._project.edition_lookup[i].label
        							+ ':<input type="text" name="edition_lookup_' 
        							+ CIT._project.edition_lookup[i].id + '" id="edition_lookup_' 
        							+ CIT._project.edition_lookup[i].id + '"/></label>');
        				}
        			}
        			html.push('<input type="button" value="find edition" id="edition_search_button"/>');
        			html.push('</fieldset>');
        			parent.innerHTML = html.join('');
        			if (typeof json !== 'undefined') {
        				for (i = 0; i < CIT._project.edition_lookup.length; i += 1) {
        					if (document.getElementById('edition_lookup_' + CIT._project.edition_lookup[i].id)) {
        						document.getElementById('edition_lookup_' + CIT._project.edition_lookup[i].id).value = json.edition_lookup[CIT._project.edition_lookup[i].id];
        					}
        				}
        			}
        			for (i = 0; i < populate.length; i += 1) {
        				criteria = {'_sort':[['_id', 1]]};
        				if (populate[i].hasOwnProperty('criteria')) {
        					for (j = 0; j < populate[i].criteria.length; j += 1) {
        						criteria[populate[i].criteria[j]] = {'$in': [CIT._project[populate[i].criteria[j]]]};
        					}
        				}
        				if (typeof json !== 'undefined' && json.hasOwnProperty('edition_lookup') && json.edition_lookup.hasOwnProperty(populate[i].id)) {
        					CIT.CIT.populate_lookup_select(populate[i], criteria, json.edition_lookup[populate[i].id]);
        				} else {
        					CIT.CIT.populate_lookup_select(populate[i], criteria);
        				}                            
        			}
        			MAG.EVENT.addEventListener(document.getElementById('edition_search_button'), 'click', function () {
        				CIT.CIT.find_edition();
        			});
        		} else {
        			//populate edition select
        			criteria = {'_sort':[['_id', 1]], 'language': CIT._project.language};
        			if (typeof json !== 'undefined' && json.hasOwnProperty('work_id')) {
        				criteria.work_id = json.work_id;
        			}
        			if (typeof json !== 'undefined' && json.hasOwnProperty('author_id')) {
        				criteria.author_id = json.author_id;
        			} else if (CIT._project.hasOwnProperty('author_ids')) {
        				criteria['_id'] = {'$in': CIT._project.author_ids};
        				if (CIT._project.author_ids.length === 1) {
        					selected = CIT._project.author_ids[0];
        				}
        			}
        			if (typeof json !== 'undefined' && json.hasOwnProperty('edition_id')) {
        				edition = json.edition_id;
        				CIT.CIT.show_edition_details(edition);
        			} else {
        				edition = 'none';
        			}
        			MAG.REST.apply_to_list_of_resources('cit_edition', {'criteria' : criteria, 'success' : function (response) {
        				MAG.FORMS.populate_select(response.results, document.getElementById('edition_id'), '_id', '_id', edition);
        			}});
        		}
        	},
        	
        	populate_lookup_select: function (details, criteria, selected) {
        	    MAG.REST.apply_to_list_of_resources(details.collection, {'criteria': criteria, 'success' :function (response) {              	
        		MAG.FORMS.populate_select(response.results, document.getElementById('edition_lookup_' + details.id), '_id', ['abbreviation', '_id'], selected);               	
                    }});        	    
        	},
        	
        	
        	find_edition: function () {
        	    var criteria, selected, i;
        	    //find the ids of the things you are looking for
        	    if (document.getElementById('work_id').value !== 'none') {
        		criteria = {'_sort':[['_id', 1]], 'language': CIT._project.language, 'work_id': document.getElementById('work_id').value};
        		for (i = 0; i < CIT._project.edition_lookup.length; i += 1) {
        		    if (document.getElementById('edition_lookup_' + CIT._project.edition_lookup[i].id) 
        			    && document.getElementById('edition_lookup_' + CIT._project.edition_lookup[i].id).value !== '') {
        			criteria[CIT._project.edition_lookup[i].id] = document.getElementById('edition_lookup_' + CIT._project.edition_lookup[i].id).value;
        		    }
        		}
        		if (CIT._project.hasOwnProperty('author_ids')) {
        		    criteria['_id'] = {'$in': CIT._project.author_ids};
        		    if (CIT._project.author_ids.length === 1) {
        			selected = CIT._project.author_ids[0];
        		    }
        		}
        		MAG.REST.apply_to_list_of_resources('cit_edition', {'criteria' : criteria, 'success' : function (editions) {
        		    if (editions.results.length === 1) {
        			MAG.FORMS.populate_select(editions.results, document.getElementById('edition_id'), '_id', '_id', editions.results[0]);
        			document.getElementById('edition_id').removeAttribute('disabled');
        			CIT.CIT.show_edition_details(editions.results[0]._id);
        		    } else if (editions.results.length > 1) {
        			MAG.FORMS.populate_select(editions.results, document.getElementById('edition_id'), '_id', '_id');       			
        			document.getElementById('edition_id').removeAttribute('disabled');
        		    } else {
        			MAG.FORMS.populate_select([{'_id': 'No Edition, add later'}], document.getElementById('edition_id'), '_id', '_id', 'No Edition, add later');
        		    }	
        		}});
        	    } else {
        		alert('You must select the work first.');
        	    }
        	},
        	
        	custom_serialize_form: function (form_id) {
                    var json, catena, parallels, i;
                    json = MAG.FORMS.serialize_form(form_id);
                    catena = []
                    for (i = 0; i < CIT.CIT.catena_count; i += 1) {
                	if (document.getElementById('biblical_catena_' + i)) {
                	    catena.push(document.getElementById('biblical_catena_' + i).innerHTML);
                	}
                    }
                    if (catena.length > 0) {
                	json.biblical_catena = catena;
                    }
                    parallels = [];
                    for (i = 0; i < CIT.CIT.parallel_count; i += 1) {
                	if (document.getElementById('biblical_parallels_' + i)) {
                	    parallels.push(document.getElementById('biblical_parallels_' + i).innerHTML);
                	}
                    }
                    if (parallels.length > 0) {
                	json.biblical_parallels = parallels;
                    }
                    if (json.hasOwnProperty('edition_id') && json.edition_id !== 'No Edition, add later') {
                	delete json['edition_lookup'];
                    }
                    return json;
                },
        	
        	get_language: function () {
        	    if (CIT._project.hasOwnProperty('language')) {
        		return CIT._project.language;
        	    } 
        	    if (document.getElementById('language') && document.getElementById('language').value !== 'none') {
        		return document.getElementById('language').value;
        	    }
        	    return null;
        	},
        	
                add_manuscript_variants: function () {
                    /*add a new line of manuscript variant boxes to fill in */
                    var html, table, newdiv, newrow, newcell, id_list, i, language;
                    language = CIT.CIT.get_language();
                    if (language === null) {
                	alert('You must select a language before continuing');
                	return;
                    }
                    
                    table = document.getElementById('MS_variants');
                    newrow = document.createElement('tr');
                    newcell = document.createElement('td');
                    newcell.setAttribute('class', 'rowhandler');
                    newcell.innerHTML = '<div class="drag row"></div>';
                    newrow.appendChild(newcell);
                    newcell = document.createElement('td');
                    newdiv = document.createElement('fieldset');
                    newdiv.setAttribute('class', 'data_group objectlist');
                    newdiv.setAttribute('id', 'manuscript_variants_' + CIT.CIT.msvariant_count);
                    
                    html = [];
                    id_list = [];
                    html.push('<label class="inline">headword:<input size="20" class="string" type="text" name="manuscript_variants_');
                    html.push(CIT.CIT.msvariant_count + '_headword" id="manuscript_variants_');
                    html.push(CIT.CIT.msvariant_count + '_headword"/></label>');
                    id_list.push('manuscript_variants_' + CIT.CIT.msvariant_count + '_headword');
                    html.push('<label class="inline inner">variant:<input size="20" class="string" type="text" name="manuscript_variants_');
                    html.push(CIT.CIT.msvariant_count + '_variant" id="manuscript_variants_');
                    html.push(CIT.CIT.msvariant_count + '_variant"/></label>');
                    id_list.push('manuscript_variants_' + CIT.CIT.msvariant_count + '_variant');
                    html.push('<label class="inline inner">MS support:<input size="15" class="string" type="text" name="manuscript_variants_');
                    html.push(CIT.CIT.msvariant_count + '_support" id="manuscript_variants_');
                    html.push(CIT.CIT.msvariant_count + '_support"/></label>');
                    id_list.push('manuscript_variants_' + CIT.CIT.msvariant_count + '_support');
                    if (language === 'lat') {
                        html.push('<label class="inline inner">vulgate?<input class="boolean" type="checkbox" name="manuscript_variants_');
                        html.push(CIT.CIT.msvariant_count + '_vulgate" id="manuscript_variants_');
                        html.push(CIT.CIT.msvariant_count + '_vulgate"/></label>');
                        id_list.push('manuscript_variants_' + CIT.CIT.msvariant_count + '_vulgate');
                    } 
                    if (language === 'grc') {
                	html.push('<label class="inline inner">maj?<input class="boolean" type="checkbox" name="manuscript_variants_');
                        html.push(CIT.CIT.msvariant_count + '_maj" id="manuscript_variants_');
                        html.push(CIT.CIT.msvariant_count + '_maj"/></label>');
                        id_list.push('manuscript_variants_' + CIT.CIT.msvariant_count + '_maj');
                    }
                    html.push('<img class="delete_logo" height="20px" width="20px" id="delete_manuscript_variants_');
                    html.push(CIT.CIT.msvariant_count + '" title="Delete this variant" src="/citations/images/delete.png"/>');
                    newdiv.innerHTML = html.join('');

                    newcell.appendChild(newdiv);
                    newrow.appendChild(newcell);
                    table.childNodes[0].appendChild(newrow);
                    MAG.EVENT.addEventListener(document.getElementById('delete_manuscript_variants_' + CIT.CIT.msvariant_count), 'click', function(event) {
                        CIT.COMCIT.delete_element(event.target.parentNode.parentNode.parentNode);
                    });
                    for (i = 0; i < id_list.length; i += 1) {
                        MAG.EVENT.addEventListener(document.getElementById(id_list[i]), 'change', function(event) {
                            CIT.validate_element(event.target);
                        });
                    }
                    CIT.COMCIT.redips_init('drag1');
                    CIT.CIT.msvariant_count += 1;
                },
                
                add_dependencies: function (data) {
                    var html, parent, newdiv;
                    parent = document.getElementById('dependencies_data_div');
                    newdiv = document.createElement('fieldset');
                    newdiv.setAttribute('class', 'data_group objectlist');
                    newdiv.setAttribute('id', 'dependencies_' + CIT.CIT.dependency_count);
                    
                    html = [];
                    html.push('<label class="inline">relationship:<select id="dependencies_');
                    html.push(CIT.CIT.dependency_count + '_relationship" name="dependencies_');
                    html.push(CIT.CIT.dependency_count + '_relationship" class="string"><option value="none">select</option><option value="is_quoted_in">is quoted in</option><option value="is_same_as">is same as</option><option value="is_quotation_of">is quotation of</option><option value="is_derived_from">is derived from</option><option value="see_also">see also</option><option value="formerly_known_as">formerly known as</option></select></label>');
                    html.push('<label class="inline inner">author:<select id="dependencies_');
                    html.push(CIT.CIT.dependency_count + '_author_id" name="dependencies_');
                    html.push(CIT.CIT.dependency_count + '_author_id" class="string"></select></label>');
                    html.push('<label class="inline inner">work:<select id="dependencies_');
                    html.push(CIT.CIT.dependency_count + '_work_id" name="dependencies_');
                    html.push(CIT.CIT.dependency_count + '_work_id" class="string"></select></label>');
                    html.push('<label class="inline inner">work reference:<input type="text" id="dependencies_');
                    html.push(CIT.CIT.dependency_count + '_work_reference" name="dependencies_');
                    html.push(CIT.CIT.dependency_count + '_work_reference" class="string"/></label>');
                    html.push('<img class="delete_logo" height="20px" width="20px" id="delete_dependency_');
                    html.push(CIT.CIT.dependency_count + '" title="Delete this dependency" src="/citations/images/delete.png"/>');
                    newdiv.innerHTML = html.join('');
                    
                    CIT.CIT.populate_dependency_selects(CIT.CIT.dependency_count, data);
                    parent.appendChild(newdiv);
                    MAG.EVENT.addEventListener(document.getElementById('delete_dependency_' + CIT.CIT.dependency_count), 'click', function(event) {
                        CIT.COMCIT.delete_element(event.target.parentNode);
                    });
                    CIT.CIT.dependency_count += 1;
                },
                
                populate_dependency_selects: function (index, data) {
                    MAG.REST.apply_to_list_of_resources('cit_author', {'criteria': {'_sort':[['abbreviation', 1]]}, 'success' : function (response) {
                	if (typeof data !== 'undefined' && data.hasOwnProperty('author_id')) {
                	    CIT.populate_select_with_obsolete(response.results, document.getElementById('dependencies_' + index + '_author_id'), '_id', {1 : 'abbreviation', 2 : 'full_name'}, data.author_id);
                	} else {
                	    CIT.populate_select_with_obsolete(response.results, document.getElementById('dependencies_' + index + '_author_id'), '_id', {1 : 'abbreviation', 2 : 'full_name'});
                	}
                        MAG.EVENT.addEventListener(document.getElementById('dependencies_' + index + '_author_id'), 'change', function() {
                            CIT.CIT.filter_works('dependencies_' + index + '_author_id', 'dependencies_' + index + '_work_id');                           
                        });
                    }});
                    MAG.REST.apply_to_list_of_resources('cit_work', {'criteria': {'_sort':[['abbreviation', 1]]}, 'success' : function (response) {
                	if (typeof data !== 'undefined' && data.hasOwnProperty('work_id')) {
                	    CIT.populate_select_with_obsolete(response.results, document.getElementById('dependencies_' + index + '_work_id'), '_id', {1: 'abbreviation', 2: 'title'}, data.work_id);
                	} else {
                	    CIT.populate_select_with_obsolete(response.results, document.getElementById('dependencies_' + index + '_work_id'), '_id', {1: 'abbreviation', 2: 'title'});
                	}
                	
                    }});
                },
                
                add_parallel: function (reference) {
                    var parent, row, table;
                    if (typeof reference === 'undefined') {
                	if (document.getElementById('book_parallel').value !== 'none' 
                	    && document.getElementById('chapter_parallel').value !== ''
                		&& document.getElementById('verse_parallel').value !== '') {
                	    reference = document.getElementById('book_parallel').value + ' ' 
                	    	+ document.getElementById('chapter_parallel').value + ':'
                	    	+ document.getElementById('verse_parallel').value;
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
                	row.innerHTML = '<td id="biblical_parallels_' + CIT.CIT.parallel_count 
                	    + '">' + reference
                	    + '</td><td><img class="delete_logo" height="15px" width="15px" id="delete_parallel_'
                	    + CIT.CIT.parallel_count
                	    + '" title="Delete this parallel" src="/citations/images/delete.png"/></td>';
                	parent.appendChild(row);
                	
                	MAG.EVENT.addEventListener(document.getElementById('delete_parallel_' + CIT.CIT.parallel_count), 'click', function (event) {
                	    if (event.target.parentNode.parentNode.parentNode.getElementsByTagName('TR').length === 1) {
                		event.target.parentNode.parentNode.parentNode.parentNode.style.display = 'none';
                	    }
                	    CIT.COMCIT.delete_element(event.target.parentNode.parentNode);
                	});
                	CIT.CIT.parallel_count += 1;
                    } else {
                	return;
                    }
                },
                
                add_catena: function (reference) {
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
                	    + CIT.CIT.catena_count + '">' 
                	    + reference
                	    + '</td><td><img class="delete_logo" height="15px" width="15px" id="delete_catena_'
                	    + CIT.CIT.catena_count
                	    + '" title="Delete this catena" src="/citations/images/delete.png"/></td>';
                	parent.appendChild(row);
                	MAG.EVENT.addEventListener(document.getElementById('delete_catena_' + CIT.CIT.catena_count), 'click', function (event) {
                	    if (event.target.parentNode.parentNode.parentNode.getElementsByTagName('TR').length === 1) {
                		event.target.parentNode.parentNode.parentNode.parentNode.style.display = 'none';
                	    }
                	    CIT.COMCIT.delete_element(event.target.parentNode.parentNode);
                	});
                	CIT.COMCIT.redips_init('drag2');
                	CIT.CIT.catena_count += 1;
                    } else {
                	return;
                    }
                },
                
                filter_works: function (seed_id, target_id) {
                    var seed;
                    seed = document.getElementById(seed_id).value;
                    MAG.REST.apply_to_list_of_resources('cit_work', {'criteria': {'author_id': seed, '_sort':[['abbreviation', 1]]}, 'success': function (response) {
                	if (response.results.length === 1) {
                	    CIT.populate_select_with_obsolete(response.results, document.getElementById(target_id), '_id', {1: 'abbreviation', 2: 'title'}, response.results[0]._id);
                	} else {
                	    CIT.populate_select_with_obsolete(response.results, document.getElementById(target_id), '_id', {1: 'abbreviation', 2: 'title'});
                	}
                    }});
                },
                
                display_extras: function () {
                    CIT.CIT.display_clavis();
                    CIT.CIT.show_edition_details();
                },
                
                show_edition_details: function (id) {
                	var editor, date, title, series, volume, superseded;
                	if (typeof id === 'undefined') {
                		id = document.getElementById('edition_id').value;
                	}
                	if (id !== 'none' && id !== '') {
                		MAG.REST.apply_to_resource('cit_edition', id, {'success': function (edition) {
                			if (edition.hasOwnProperty('editor')) {
                				editor = edition.editor + ' ';
                			} else {
                				editor = '';
                			}
                			if (edition.hasOwnProperty('date')) {
                				date = '(' + edition.date + ') ';
                			} else {
                				date = '';
                			}
                			if (edition.hasOwnProperty('independent_title')) {
                				title = '<i>' + edition.independent_title + '.</i> ';
                			} else {
                				title = '';
                			}
                			if (edition.hasOwnProperty('series_id')) {
                				series = edition.series_id + ' ';
                			} else {
                				series = '';
                			}
                			if (edition.hasOwnProperty('volume')) {
                				volume = edition.volume + '.';
                			} else {
                				volume = '.';
                			}   
                			if (edition.hasOwnProperty('superseded')) {
                				superseded = ' (superseded)';
                			} else {
                				superseded = '';
                			}
                			document.getElementById('edition_details').innerHTML = editor + date + title + series + volume + superseded;
                		}});
                	} else {
                		document.getElementById('edition_details').innerHTML = '';
                	}
                },

                display_clavis: function () {
                    if (document.getElementById('work_id').value !== 'none') {
                        MAG.REST.apply_to_resource('cit_work', document.getElementById('work_id').value, {'success': function (response) {
                            	if (response.hasOwnProperty('clavis')) {
                            	    document.getElementById('clavis_check').innerHTML = 'Clavis: ' + response.clavis;
                            	} else {
                            	    document.getElementById('clavis_check').innerHTML = 'No clavis';
                            	}
                            }, 'error' : function () {
                        	document.getElementById('clavis_check').innerHTML = '';
                        }});               	
                    } else {
                	document.getElementById('clavis_check').innerHTML = '';
                    }
                },
            }
        }()),


        COMCIT: (function () {
            return {
        	
        	lemma_headword_count: 1,
                lemma_extent_count: 1,
                lemma_msvariant_count: 1,
                other_references_count: 1,

                redips_init: function (id) {
                    // reference to the REDIPS.drag library and message line
                    var rd = REDIPS.drag;
                    rd.init(id);
                },

                get_basetext: function (model, json) {
                	/* check that the book, chapter and verse boxes all contain a value and then retrieve relevant basetext*/
                	/* this should be specified in the project but we need a default for each language in case it is not*/
                	var book, chapter, verse, language, text, siglum, label;
                	if (typeof json === 'undefined') {
                		book = 'none';
                		chapter = '';
                		verse = '';
                		language = 'none';
                		if (document.getElementById('book')) {
                			book = document.getElementById('book').value;
                			if (book !== 'none') {
                				book = parseInt(book);
                			}
                		}
                		if (document.getElementById('chapter')) {
                			chapter = document.getElementById('chapter').value;
                			if (chapter !== '') {
                				chapter = parseInt(chapter);
                			}
                		}
                		if (document.getElementById('verse')) {
                			verse = document.getElementById('verse').value;
                			if (verse !== '') {
                				verse = parseInt(verse);
                			}
                		}
                		if (document.getElementById('language')) {
                			language = document.getElementById('language').value;
                		}
                	} else {
                		book = json.book;
                		chapter = json.chapter;
                		verse = json.verse;
                		language = json.language;
                	}
                	//if we have all the data that we need
                	if (book !== 'none' && chapter !== '' && verse !== '' && language !== 'none') {
                		//check project infomation
                		if (CIT._project.hasOwnProperty('base_text')) {
                			siglum = CIT._project.base_text.siglum;
                			label = CIT._project.base_text.label;
                		} else {
                			if (document.getElementById('language').value == 'grc') {
                				siglum = 'TR';
                				label = 'TR';
                			}
                			if (document.getElementById('language').value == 'lat') {
                				siglum = 'vg^st5';
                				label = 'Vulgate';
                			}
                		}
                		MAG.REST.apply_to_list_of_resources('verse',
                				{'criteria' : {'siglum': siglum, 'book_number': book, 'chapter_number': chapter, 'verse_number': verse},
                			'success' : function (response){
                				if (response.results[0] !== undefined) {
                					document.getElementById('basetext_label').innerHTML = label + ' text:'
                					text = response.results[0].tei;
                					document.getElementById('basetext_text').innerHTML = CIT.COMCIT.strip_tags(text);
                					if (model === 'cit_comcitation') {
                						if (typeof json === 'undefined' || !json.hasOwnProperty('lemma')) {
                							document.getElementById('lemma_text').value = CIT.COMCIT.strip_tags(text);
                							document.getElementById('exegesis_text').value = CIT.COMCIT.strip_tags(text);
                							document.getElementById('lemma_text_reminder').innerHTML = CIT.COMCIT.strip_tags(text);
                						}
                					}                                       
                				} else {
                					document.getElementById('basetext_text').innerHTML = '';
                					document.getElementById('basetext_label').innerHTML = '';
                					alert('there is no base text available for this verse');
                					//TODO: decide whether transcribers are permitted to continue without a base text or not.
                				}
                			}});
                	}
                },
                
                //TODO: think about losing punctuation here (TR in particular)
                strip_tags: function (string) {
                    var tag_regex;
                    tag_regex = /<.+?>/g;
                    return MAG.TEMPLATE.trim(string.replace(tag_regex, ' ').replace(/\n|\r|\t/g, ' '));
                },

                update_lemma_reminder: function (lemma_text) {
                    document.getElementById('lemma_text_reminder').innerHTML = lemma_text;
                },
                
                update_exegesis_text: function (lemma_text) {
                    if (document.getElementById('reconstruction_checkbox').checked === false){
                        document.getElementById('exegesis_text').value = lemma_text;
                    }                        
                },

                add_lemma_exegesis_diffs: function () {
                    /*add a new line of boxes to fill in */
                    var addlink, table, newrow, newcell, newdiv, id_list, i;
                    table = document.getElementById('lemma_ex_diffs');
                    newrow = document.createElement('tr');
                    newcell = document.createElement('td');
                    newcell.setAttribute('class', 'rowhandler');
                    newcell.innerHTML = '<div class="drag row"></div>';
                    newrow.appendChild(newcell);
                    newcell = document.createElement('td');
                    newdiv = document.createElement('fieldset');
                    newdiv.setAttribute('class', 'data_group objectlist');
                    newdiv.setAttribute('id', 'lemma_exegesis_diffs_' + CIT.COMCIT.lemma_headword_count);
                    newdiv.innerHTML = '<label class="inline float">Headword:<input name="lemma_exegesis_diffs_'
                        + CIT.COMCIT.lemma_headword_count + '_headword" id="lemma_exegesis_diffs_'
                        + CIT.COMCIT.lemma_headword_count + '_headword" type="text" size="15" class="lemma_exegesis_diffs string"/></label>'

                        + '<fieldset id="lemma_exegesis_diffs_'
                        + CIT.COMCIT.lemma_headword_count + '_difference" class="data_group float">'
                        + '<label class="inline inner">Difference:<input name="lemma_exegesis_diffs_'
                        + CIT.COMCIT.lemma_headword_count + '_difference_text" id="lemma_exegesis_diffs_'
                        + CIT.COMCIT.lemma_headword_count + '_difference_text" type="text" size="15" class="string"/></label>'
                        + '<label id="location_label" class="inline inner">Location:<input name="lemma_exegesis_diffs_'
                        + CIT.COMCIT.lemma_headword_count + '_difference_location" id="lemma_exegesis_diffs_'
                        + CIT.COMCIT.lemma_headword_count + '_difference_location" type="text" size="1" class="string"/></label>'
                        + '<label class="inline inner">Ed.? </label><input type="checkbox" name="lemma_exegesis_diffs_'
                        + CIT.COMCIT.lemma_headword_count + '_difference_editorial" id="lemma_exegesis_diffs_'
                        + CIT.COMCIT.lemma_headword_count + '_difference_editorial" class="boolean checkbox"/></label>'
                        + '<label class="inline inner">MS support:<input name="lemma_exegesis_diffs_'
                        + CIT.COMCIT.lemma_headword_count + '_difference_mssupport" id="lemma_exegesis_diffs_'
                        + CIT.COMCIT.lemma_headword_count + '_difference_mssupport" type="text" size="10" class="string inner_input"/></label>'
                        + '</fieldset>'

                        + '<img id="delete_lemma_headword_'
                        + CIT.COMCIT.lemma_headword_count + '" class="delete_logo float" height="20px" width="20px"  title="Delete this line" src="/citations/images/delete.png"/>'
                        + '<br/><fieldset id="lemma_exegesis_diffs_'
                        + CIT.COMCIT.lemma_headword_count + '_mainvariant" class="data_group lower">'
                        + '<label id="mainvariant_label" class="inline">Main variant:<input name="lemma_exegesis_diffs_'
                        + CIT.COMCIT.lemma_headword_count + '_mainvariant_text" id="lemma_exegesis_diffs_'
                        + CIT.COMCIT.lemma_headword_count + '_mainvariant_text" type="text" size="15" class="string"/></label>'
                        + '<label class="inline inner">MS support:<input name="lemma_exegesis_diffs_'
                        + CIT.COMCIT.lemma_headword_count + '_mainvariant_mssupport" id="lemma_exegesis_diffs_'
                        + CIT.COMCIT.lemma_headword_count + '_mainvariant_mssupport" type="text" size="10" class="string"/></label>'
                        + '<label class="inline inner">Alternatives and attestation:<input id="lemma_exegesis_diffs_'
                        + CIT.COMCIT.lemma_headword_count + '_mainvariant_alternatives" name="lemma_exegesis_diffs_'
                        + CIT.COMCIT.lemma_headword_count + '_mainvariant_alternatives" type="text" size="20" class="string"/></label>'
                        + '<label class="inline inner">PP?:<input id="lemma_exegesis_diffs_'
                        + CIT.COMCIT.lemma_headword_count + '_mainvariant_difference_possible_paraphrase" name="lemma_exegesis_diffs_'
                        + CIT.COMCIT.lemma_headword_count + '_mainvariant_difference_possible_paraphrase" type="checkbox" class="boolean checkbox"/></label>'
                        + '</fieldset>';
                    //TODO: this PP? thing and whole datastructure need looking at as name or id didn't have _mainvariant_difference 
                    // in before and the ticks were being lost. Need to decide what datastructure should be and fix and then check all existing data to ensure nothing is lost
                    newcell.appendChild(newdiv);
                    newrow.appendChild(newcell);
                    table.childNodes[0].appendChild(newrow);
                    //add handlers
                    MAG.EVENT.addEventListener(document.getElementById('delete_lemma_headword_' + CIT.COMCIT.lemma_headword_count), 'click', function(event){
                        CIT.COMCIT.delete_element(event.target.parentNode.parentNode.parentNode);
                    });
                    id_list = ['lemma_exegesis_diffs_' + CIT.COMCIT.lemma_headword_count + '_headword',
                               'lemma_exegesis_diffs_' + CIT.COMCIT.lemma_headword_count + '_difference_text',
                               'lemma_exegesis_diffs_' + CIT.COMCIT.lemma_headword_count + '_difference_location',
                               'lemma_exegesis_diffs_' + CIT.COMCIT.lemma_headword_count + '_difference_editorial',
                               'lemma_exegesis_diffs_' + CIT.COMCIT.lemma_headword_count + '_difference_mssupport',
                               'lemma_exegesis_diffs_' + CIT.COMCIT.lemma_headword_count + '_mainvariant_text',
                               'lemma_exegesis_diffs_' + CIT.COMCIT.lemma_headword_count + '_mainvariant_mssupport',
                               'lemma_exegesis_diffs_' + CIT.COMCIT.lemma_headword_count + '_mainvariant_alternatives'
                               ];
                    for (i = 0; i < id_list.length; i += 1) {
                        MAG.EVENT.addEventListener(document.getElementById(id_list[i]), 'change', function(event){
                            CIT.validate_element(event.target);
                        });
                    }
                    CIT.COMCIT.redips_init('drag2');
                    CIT.COMCIT.lemma_headword_count += 1;
                },

                add_other_references: function () {
                    var table, newrow, newcell, newdiv;
                    table = document.getElementById('other_refs_table');
                    newrow = document.createElement('tr');
                    newcell = document.createElement('td');
                    newcell.setAttribute('class', 'rowhandler');
                    newcell.innerHTML = '<div class="drag row"></div>';
                    newrow.appendChild(newcell);
                    newcell = document.createElement('td');
                    newdiv = document.createElement('fieldset');
                    newdiv.setAttribute('class', 'data_group objectlist');
                    newdiv.setAttribute('id', 'other_references_' + CIT.COMCIT.other_references_count);
                    newdiv.setAttribute('name', 'other_references_' + CIT.COMCIT.other_references_count);
                    newdiv.innerHTML = '<label class="top width_half">Location:<input type="text" id="other_references_'
                       + CIT.COMCIT.other_references_count + '_location" name="other_references_'
                       + CIT.COMCIT.other_references_count + '_location"/></label>'
                       + '<label class="top width_half">Text:<input type="text" id="other_references_'
                       + CIT.COMCIT.other_references_count + '_text" name="other_references_'
                       + CIT.COMCIT.other_references_count + '_text"/></label>'
                       + '<label class="top width_quarter checkbox_label">Identical to Lemma?<input type="checkbox" class="boolean" id="other_references_'
                       + CIT.COMCIT.other_references_count + '_as_lemma" name="other_references_'
                       + CIT.COMCIT.other_references_count + '_as_lemma"/></label>'
                       + '<label class="top width_half">Comment:<input type="text" id="other_references_'
                       + CIT.COMCIT.other_references_count + '_comment" name="other_references_'
                       + CIT.COMCIT.other_references_count + '_comment"/></label>'
                       + '<img class="delete_logo" height="20px" width="20px" id="delete_other_references_'
                       + CIT.COMCIT.other_references_count + '" title="Delete this reference" src="/citations/images/delete.png"/>';
                    newcell.appendChild(newdiv);
                    newrow.appendChild(newcell);
                    table.childNodes[0].appendChild(newrow);
                    MAG.EVENT.addEventListener(document.getElementById('delete_other_references_' + CIT.COMCIT.other_references_count), 'click', function(event){
                        CIT.COMCIT.delete_element(event.target.parentNode.parentNode.parentNode);
                    });
                    CIT.COMCIT.redips_init('drag3');
                    CIT.COMCIT.other_references_count += 1;
                },

                add_lemma_msvariant: function () {
                    /*add a new line of lemma variant boxes to fill in */
                    var table, newdiv, newrow, newcell, id_list, i;
                    table = document.getElementById('MS_variants');
                    newrow = document.createElement('tr');
                    newcell = document.createElement('td');
                    newcell.setAttribute('class', 'rowhandler');
                    newcell.innerHTML = '<div class="drag row"></div>';
                    newrow.appendChild(newcell);
                    newcell = document.createElement('td');
                    newdiv = document.createElement('fieldset');
                    newdiv.setAttribute('class', 'data_group objectlist lemma_msvariant');
                    newdiv.setAttribute('id', 'lemma_msvariant_' + CIT.COMCIT.lemma_msvariant_count);
                    newdiv.innerHTML = '<label class="inline">headword:<input size="20" class="string" type="text" name="lemma_msvariant_'
                        + CIT.COMCIT.lemma_msvariant_count + '_headword" id="lemma_msvariant_'
                        + CIT.COMCIT.lemma_msvariant_count + '_headword"/></label>\n'
                        + '<label class="inline inner">variant:<input size="20" class="string" type="text" name="lemma_msvariant_'
                        + CIT.COMCIT.lemma_msvariant_count + '_variant" id="lemma_msvariant_'
                        + CIT.COMCIT.lemma_msvariant_count + '_variant"/></label>\n'
                        + '<label class="inline inner">MS support:<input size="15" class="string" type="text" name="lemma_msvariant_'
                        + CIT.COMCIT.lemma_msvariant_count + '_support" id="lemma_msvariant_'
                        + CIT.COMCIT.lemma_msvariant_count + '_support"/></label>\n'
                        + '<label class="inline inner">vulgate?<input class="boolean" type="checkbox" name="lemma_msvariant_'
                        + CIT.COMCIT.lemma_msvariant_count + '_vulgate" id="lemma_msvariant_'
                        + CIT.COMCIT.lemma_msvariant_count + '_vulgate"/></label>'
                        + '<img class="delete_logo" height="20px" width="20px" id="delete_lemma_msvariant_'
                        + CIT.COMCIT.lemma_msvariant_count + '" title="Delete this variant" src="/citations/images/delete.png"/>';
                    newcell.appendChild(newdiv);
                    newrow.appendChild(newcell);
                    table.childNodes[0].appendChild(newrow);
                    MAG.EVENT.addEventListener(document.getElementById('delete_lemma_msvariant_' + CIT.COMCIT.lemma_msvariant_count), 'click', function(event){
                        CIT.COMCIT.delete_element(event.target.parentNode.parentNode.parentNode);
                    });
                    id_list = ['lemma_msvariant_' + CIT.COMCIT.lemma_msvariant_count + '_headword',
                               'lemma_msvariant_' + CIT.COMCIT.lemma_msvariant_count + '_variant',
                               'lemma_msvariant_' + CIT.COMCIT.lemma_msvariant_count + '_support',
                               'lemma_msvariant_' + CIT.COMCIT.lemma_msvariant_count + '_vulgate'];
                    for (i = 0; i < id_list.length; i += 1) {
                        MAG.EVENT.addEventListener(document.getElementById(id_list[i]), 'change', function(event){
                            CIT.validate_element(event.target);
                        });
                    }
                    CIT.COMCIT.redips_init('drag1');
                    CIT.COMCIT.lemma_msvariant_count += 1;
                },

                add_lemma_extent: function () {
                    /*add a new line of lemma boxes to fill in */
                    var addlink, parent, newdiv, id_list, i;
                    addlink = document.getElementById('add_lemma_extent');
                    parent = addlink.parentNode;
                    newdiv = document.createElement('fieldset');
                    newdiv.setAttribute('class', 'data_group objectlist lemma_extent');
                    newdiv.setAttribute('id', 'lemma_extent_' + CIT.COMCIT.lemma_extent_count);
                    newdiv.innerHTML = '<label class="inline">start:<input id="lemma_extent_'
                        + CIT.COMCIT.lemma_extent_count + '_start" name="lemma_extent_'
                        + CIT.COMCIT.lemma_extent_count + '_start" type="text" size="10"/></label>'
                        + '<label class="inline inner">end:<input id="lemma_extent_'
                        + CIT.COMCIT.lemma_extent_count + '_end" name="lemma_extent_'
                        + CIT.COMCIT.lemma_extent_count + '_end" type="text" size="10"/></label>'
                        + '<img class="delete_logo" height="20px" width="20px" id="delete_lemma_'
                        + CIT.COMCIT.lemma_extent_count + '" title="Delete this lemma" src="/citations/images/delete.png"/>';
                    parent.insertBefore(newdiv, addlink);
                    //add handlers
                    MAG.EVENT.addEventListener(document.getElementById('delete_lemma_' + CIT.COMCIT.lemma_extent_count), 'click', function(event){
                        CIT.COMCIT.delete_element(event.target.parentNode);
                    });
                    id_list = ['lemma_extent_' + CIT.COMCIT.lemma_extent_count + '_start', 'lemma_extent_' + CIT.COMCIT.lemma_extent_count + '_end'];
                    for (i = 0; i < id_list.length; i += 1) {
                        MAG.EVENT.addEventListener(document.getElementById(id_list[i]), 'change', function(event){
                            CIT.validate_elem_regex(event.target, /^\d{1,2}:\d{1,2}[a-z]?$/);
                        });
                    }
                    CIT.COMCIT.lemma_extent_count += 1;
                },

                delete_element: function (elem) {
                    elem.parentNode.removeChild(elem);
                },
            };
        }()),

        //a special version based on DISPLAY version which also deals with dependencies,
        //this is kept separate as dependencies for other applications cannot be predicted
        show_instance_table: function (json, container_id, options, deps) {
            var container, html, show_blanks, deps, deps_html;
            container = document.getElementById(container_id) || document.getElementsByTagName('body')[0];
            html = [];
            show_blanks = options.blanks || false;
            if (deps === undefined) {
                deps = {};
            }
            if (options !== undefined && options.key_order !== undefined) {
                html = MAG.DISPLAY.create_instance_table(json, options.key_order, show_blanks);
                deps_html = CIT.get_deps_rows(deps);
                container.innerHTML = '<table class="data_instance">' + html.join('') + deps_html.join('') + '</table>';
            } else if (json.hasOwnProperty('_view') && json._view.hasOwnProperty('instance')) {
                html = MAG.DISPLAY.create_instance_table(json, json._view.instance, show_blanks);
                deps_html = CIT.get_deps_rows(deps);
                container.innerHTML = '<table class="data_instance">' + html.join('') + deps_html.join('') + '</table>';
            } else {
                MAG.REST.apply_to_resource('_model', json._model, {'success' : function (response) {
                    if (response.hasOwnProperty('_view') && response._view.hasOwnProperty('instance')) {
                        html = MAG.DISPLAY.create_instance_table(json, response._view.instance, show_blanks);
                        deps_html = CIT.get_deps_rows(deps);
                        container.innerHTML = '<table class="data_instance">' + html.join('') + deps_html.join('') + '</table>';
                    }
                }});
            }
        },

        get_deps_rows: function(deps) {
            var i, j, html;
            html = [];
            if (deps.hasOwnProperty('order')) {
                for (i = 0; i < deps.order.length; i += 1) {
                    html.push('<tr>');
                    html.push('<td class="label level0">' + MAG.DISPLAY.capitalise_titles(deps.order[i]) + '</td>');
                    html.push('<td class="data">');
                    for (j = 0; j < deps[deps.order[i]].length; j += 1) {
                        html.push('<a href="/citations/' + deps.order[i].replace(CIT.model_namespace, '') + '/?'
                                + deps.order[i].replace(CIT.model_namespace, '') + '=' + deps[deps.order[i]][j].id + '">'
                                + deps[deps.order[i]][j].display + '</a>' + '<br/>');
                    }
                    html.push('</td>');
                    html.push('</tr>');
                }
                return html;
            }
            else {
                return html;
            }
        },

/*************************************************************************************
 * History functions
 */

        display_historical_object: function () {
            var param_dict;
            param_dict = MAG.URL.get_current_query();
            if (param_dict.hasOwnProperty('_history')) {
                MAG.REST.get_history_item(param_dict['_history'], param_dict['type'], { 'success': function(json) {
                    document.getElementById('title').innerHTML = 'Version ' + json.document._meta._version +  ' of ' + MAG.DISPLAY.capitalise_titles(param_dict['type']) + ' ' + json.document_id;
                    MAG.DISPLAY.show_instance_table(json.document, 'content', {'blanks': true});
                }});
            }
        },

        toggle_history: function (model) {
            var button, id;
            button = document.getElementById('history_button');
            if (document.getElementById('history').style.display === 'block') {
        	document.getElementById('history').style.display = 'none';
                document.getElementById('history_button').value = 'Show history';
            } else {
        	id = document.getElementById('_id').value;
                MAG.REST.get_history_for_instance(model, id, {'force_reload': true, 'success': function(response){
                    if (response.results.length > 0) {
                        document.getElementById('history').innerHTML = CIT.process_history(response.results, model);
                    } else {
                        document.getElementById('history').innerHTML = 'There is no history for this object.';
                    }
                    document.getElementById('history').style.display = 'block';
                    button = document.getElementById('history_button');
                    button.value = 'Hide history';
                }});
            } 
        },
        

        process_history: function (json, model) {
            var i, output, date;
            output = [];
            for (i = 0; i < json.length; i += 1) {
                date = new Date(json[i].document._meta._last_modified_time.$date);
                output.push(json[i].document._meta._version + '. ' + date.getDate() + '/' + (date.getMonth() + 1) + '/' + date.getFullYear() + ' ' + json[i].comment + ' by ' + json[i].document._meta._last_modified_by_display
                        + ' <a href="/citations/_history/?_history=' + json[i]._id + '&type=' + model + '" target="_blank">View</a>');
            }
            return output.join('<br/>');
        },

        enable_formfield: function (checkbox_id, form_field_id) {
            var checkbox;
            checkbox = document.getElementById(checkbox_id);
            if (checkbox.checked === true) {
                document.getElementById(form_field_id).disabled = false;
            } else {
                document.getElementById(form_field_id).disabled = true;
            }
        },

        toggle_ms_edition: function (caller_id) {
            if (caller_id === 'is_ms') {
                if (document.getElementById('is_ms').checked === true) {
                    document.getElementById('ms_siglum').disabled = false;
                    document.getElementById('edition_id').disabled = true;
                } else {
                    document.getElementById('ms_siglum').disabled = true;
                    document.getElementById('edition_id').disabled = false;
                }
            }
        },
        
        filterData: function (id, value, inc_obsolete, callback) {
            var criteria, reactivate;
            if (typeof inc_obsolete === 'undefined') {
                inc_obsolete = true;
            }
            //for populating work based on author this will sometimes then call this again for the work setting
            if (id === 'author_id' && document.getElementById('work_id') !== null) {
                edit.populateWork('edition', {'author': value, 'inc_obsolete': inc_obsolete}, function () {
                	CIT.filter_data('work_id', select, inc_obsolete, callback);                   
                    CIT.validate_element(document.getElementById('work_id'));
                });
//            	
//            	reactivate = false;
//                criteria = {'_sort': 'abbreviation'};
//                if (inc_obsolete === false) {
//                    criteria['obsolete'] = {'$exists': false};
//                }
//                if (value !== 'none') {
//                	criteria.author_id = value;
//                	reactivate = true;
//                }
//                MAG.REST.apply_to_list_of_resources('cit_work', {'criteria': criteria, 'success' : function(response) {
//                	var select;
//                	if (response.results.length === 1) {
//                		select = response.results[0]._id;
//                	} else {
//                		select = 'none';
//                	}
//                    CIT.populate_select_with_obsolete(response.results, document.getElementById('work_id'), '_id', {1 : 'abbreviation', 2 : 'title'}, select, undefined, reactivate);
//                    CIT.filter_data('work_id', select, inc_obsolete, callback);                   
//                    CIT.validate_element(document.getElementById('work_id'));
//                }});
            //for populating editions based on work
            } else if (id === 'work_id' 
            			&& document.getElementById('edition_id') !== null 
            			&& document.getElementById('edition_id').disabled !== true) {
            	criteria = {'_sort':[['editor', 1]]};
            	if (value !== 'none') {
            		criteria.work_id = value;
            	}
                MAG.REST.apply_to_list_of_resources('cit_edition', {'criteria': criteria, 'success' : function (response) {
                    var select;
                    if (response.results.length === 1) {
                    	select = response.results[0]._id;
                    } else {
                    	select = 'none';
                    }
                    MAG.FORMS.populate_select(response.results, document.getElementById('edition_id'), '_id', '_id', select);
                    CIT.validate_element(document.getElementById('edition_id'));
                    if (typeof callback !== 'undefined') {
                    	callback();
                    }
                }});  
            }
        },

        filter_data: function (id, value, inc_obsolete, callback) {
            var criteria, reenable;
            if (typeof inc_obsolete === 'undefined') {
                inc_obsolete = true;
            }
            if (id === 'author_id') {
                if (document.getElementById('work_id') !== null) {
                    reenable = false;
                    if (value !== 'none') {
                        criteria = {'author_id': value, '_sort':[['abbreviation', 1]]};
                        if (inc_obsolete === false) {
                            criteria['obsolete'] = {'$exists': false};
                        }
                        if (criteria.hasOwnProperty('author_id')) {
                            reenable = true;
                        }
                        MAG.REST.apply_to_list_of_resources('cit_work', {'criteria': criteria, 'success' : function(response) {
                            if (response.results.length === 1) {
                                if (inc_obsolete === true) {
                                    CIT.populate_select_with_obsolete(response.results, document.getElementById('work_id'), '_id', {1 : 'abbreviation', 2 : 'title'}, response.results[0]._id, reenable);
                                } else {
                                    MAG.FORMS.populate_select(response.results, document.getElementById('work_id'), '_id', {1 : 'abbreviation', 2 : 'title'}, response.results[0]._id, undefined, reenable);
                                }
                                CIT.filter_data('work_id', response.results[0]._id, inc_obsolete, callback);
                                CIT.validate_element(document.getElementById('work_id'));
                                if (document.getElementById('identifier').disabled === false){
                                    CIT.update_identifier(document.getElementById('_model').value);
                                }
                            } else {
                                CIT.populate_select_with_obsolete(response.results, document.getElementById('work_id'), '_id', {1 : 'abbreviation', 2 : 'title'}, undefined, reenable);
                                CIT.filter_data('work_id', 'none', inc_obsolete, callback);
                                CIT.validate_element(document.getElementById('work_id'));
                                if (document.getElementById('identifier').disabled === false){
                                    CIT.update_identifier(document.getElementById('_model').value);
                                }
                            }
                        }});
                    } else {
                        criteria = {'_sort':[['abbreviation', 1]]};
                        if (inc_obsolete === false) {
                            criteria['obsolete'] = {'$exists': false};
                        }
                        MAG.REST.apply_to_list_of_resources('cit_work', {'criteria': criteria, 'success' : function(response) {
                            if (inc_obsolete === true) {
                                CIT.populate_select_with_obsolete(response.results, document.getElementById('work_id'), '_id', {1 : 'abbreviation', 2 : 'title'}, undefined, reenable);
                            } else {
                                MAG.FORMS.populate_select(response.results, document.getElementById('work_id'), '_id', {1 : 'abbreviation', 2 : 'title'}, undefined, undefined, reenable);
                            }
                            CIT.filter_data('work_id', 'none', inc_obsolete, callback);
                            CIT.validate_element(document.getElementById('work_id'));
                            if (document.getElementById('identifier').disabled === false) {
                                CIT.update_identifier(document.getElementById('_model').value);
                            }['abbreviation', 'title', '_id']
                        }});
                    }
                }
            } else if (id === 'work_id') {
                if (document.getElementById('edition_id') !== null && document.getElementById('edition_id').disabled !== true) {
                    if (value !== 'none') {
                        MAG.REST.apply_to_list_of_resources('cit_edition', {'criteria': {'_sort':[['editor', 1]], 'work_id': value}, 'success' : function (response) {
                            if (response.results.length === 1) {
                                MAG.FORMS.populate_select(response.results, document.getElementById('edition_id'), '_id', '_id', response.results[0]._id);
                                CIT.validate_element(document.getElementById('edition_id'));
                                if (document.getElementById('identifier').disabled === false){
                                    CIT.update_identifier(document.getElementById('_model').value);
                                }
                            } else {
                                MAG.FORMS.populate_select(response.results, document.getElementById('edition_id'), '_id', '_id');
                                CIT.validate_element(document.getElementById('edition_id'));
                                if (document.getElementById('identifier').disabled === false){
                                    CIT.update_identifier(document.getElementById('_model').value);
                                }
                            }
                            if (typeof callback !== 'undefined') {
                        	callback();
                            }
                        }});
                    } else {
                        MAG.REST.apply_to_list_of_resources('cit_edition', {'criteria': {'_sort':[['editor', 1]]}, 'success' : function (response) {
                            MAG.FORMS.populate_select(response.results, document.getElementById('edition_id'), '_id', '_id');
                            CIT.validate_element(document.getElementById('edition_id'));
                            if (document.getElementById('identifier').disabled === false){
                                CIT.update_identifier(document.getElementById('_model').value);
                            }
                            if (typeof callback !== 'undefined') {
                        	callback();
                            }
                        }});
                    }
                }
            }
        },

        populate_select_with_obsolete: function (data, select, value_key, text_keys, selected_option_value, reenable) {
            var options, i, j, template, mapping, text_key, inner_template, inner_template_list, option_text, inner_mapping;
            options = '<option value="none">select</option>';
            template = '<option value="{val}"{className}{select}>{text}</option>';
            for (i = 0; i < data.length; i += 1) {
                if (MAG.TYPES.is_array(text_keys)) {
                    for (j = 0; j < text_keys.length; j += 1) {
                        if (data[i].hasOwnProperty(text_keys[j])) {
                            text_key = text_keys[j];
                            break;
                        }
                    }
                } else {
                    text_key = text_keys;
                }
                if (MAG.TYPES.is_object(text_key)) {
                    inner_template_list = [];
                    j = 1;
                    inner_mapping = {};
                    while (text_key.hasOwnProperty(j)) {
                        inner_template_list.push('{' + text_key[j] + '}');
                        inner_template = inner_template_list.join(', ');
                        inner_mapping[text_key[j]] = 'test';
                        inner_mapping[text_key[j]] = data[i][text_key[j]] || 'none';
                        j += 1;
                    }
                    option_text = MAG.TEMPLATE.substitute(inner_template, inner_mapping);
                }
                mapping = {val: data[i][value_key], text: option_text || data[i][text_key] || ' ', select: "", className: ''};
                if (selected_option_value !== 'undefined' && data[i][value_key] === selected_option_value) {
                    mapping.select = ' selected="selected"';
                }
                if (data[i].hasOwnProperty('obsolete')) {
                    mapping.className = ' class="obsolete"';
                }
                options += MAG.TEMPLATE.substitute(template, mapping);
            }
            select.innerHTML = options;
            if (reenable === true) {
        	select.disabled = false;
            }
        },

        confirm_delete: function(model) {
            var id;
            id = document.getElementById('_id').value;
            CIT.get_dependencies(model, id, 'CIT.display_delete_dependencies');
        },

        display_delete_dependencies: function(dependencies){
            var form, body, div, i, j, column, ul, confirm;
            form = document.getElementsByTagName('form')[0];
            body = document.getElementById('container');
            body.removeChild(form);
            document.getElementById('page_title').innerHTML = 'Confirm Delete';
            div = document.createElement('div');
            div.innerHTML = 'Are you sure you want to delete the ' + dependencies.seed_model.replace(CIT.model_namespace, '') + ' with the id ' + dependencies.seed_id + '?';
            if (dependencies.hasOwnProperty('order') && dependencies.order.length > 0) {
                div.innerHTML += '<br/><br/>This object has the following dependencies:<br/>';
                for (i = 0; i < dependencies.order.length; i += 1) {
                    column = document.createElement('div');
                    column.setAttribute('class', 'dep_column');
                    column.setAttribute('id', dependencies.order[i]);
                    if (dependencies.primary.indexOf(dependencies.order[i]) !== -1) {
                	column.innerHTML = '<span class="column_title">' 
                	    + MAG.DISPLAY.capitalise_titles(dependencies.order[i].replace(CIT.model_namespace, '')) 
                	    + 's (will be deleted)</span><br/>';
                    } else {
                	column.innerHTML = '<span class="column_title">' 
                	    + MAG.DISPLAY.capitalise_titles(dependencies.order[i].replace(CIT.model_namespace, '')) 
                	    + 's (will have links to deleted object(s) removed)</span><br/>';
                    }
                    ul = document.createElement('ul');
                    for (j = 0; j < dependencies[dependencies.order[i]].length; j += 1) {
                	// use to add links to dependencies deletion list commented out line (taken out for now because seems excessive)
                	//ul.innerHTML += '<li><a href="/citations/' + dependencies.order[i].replace(CIT.model_namespace, '') + '?' + dependencies.order[i].replace(CIT.model_namespace, '') + '=' + dependencies[dependencies.order[i]][j].id + '" target="_blank">' + dependencies[dependencies.order[i]][j].id + '</a></li>';
                	ul.innerHTML += '<li>' + dependencies[dependencies.order[i]][j].id + '</li>';
                    }
                    column.appendChild(ul);
                    div.appendChild(column);
                }
            } else {
                div.innerHTML += '<br/><br/>This object has no dependencies.<br/>';
                
            }
            confirm = document.createElement('div');
            confirm.setAttribute('id', 'confirm_buttons');
            confirm.innerHTML = '<br/><input id="delete_all" type="button" value="Confirm delete"/>';
            confirm.innerHTML += '<input id="cancel_delete" type="button" value="Cancel and return to previous page"/>';
            div.appendChild(confirm);
            body.appendChild(div);
            MAG.EVENT.addEventListener(document.getElementById('cancel_delete'), 'click', function(){
                location.reload();
            });
            MAG.EVENT.addEventListener(document.getElementById('delete_all'), 'click', function(){
                CIT.get_dependencies(dependencies.seed_model, dependencies.seed_id, 'CIT.delete_object_and_deps');
            });
        },

        delete_object_and_deps: function (deps) {
            var i, j, json, id_list, json_list, ids;
            //step through and sort out deleting
            //remember to include permissions checking for all models
            //if you can't delete or update necessary models then
            //you cannot delete this object
            switch (deps.seed_model) {
            case 'cit_author':
                MAG.AUTH.check_permissions({'cit_author': ['delete'], 'cit_work': ['delete'], 'cit_edition': ['delete'], 'cit_comcitation': ['delete']}, {'success': function (response) {
                    if (response[0] === true) {
                        MAG.REST.delete_resource(deps.seed_model, deps.seed_id);
                        for (i = 0; i < deps.order.length; i += 1) {
                            ids = [];
                            for (j = 0; j < deps[deps.order[i]].length; j += 1) {
                                ids.push(deps[deps.order[i]][j].id);
                            }
                            MAG.REST.delete_resources(deps.order[i], ids);                            
                        }
                        window.location = '/citations/author/';
                    } else {
                        CIT.handle_error('delete', 401, 'cit_author');
                    }
                }});
                break;
            case 'cit_work':
                MAG.AUTH.check_permissions({'cit_work': ['delete'], 'cit_edition': ['delete'], 'cit_comcitation': ['delete']}, {'success': function(response) {
                    if (response[0] === true) {
                        MAG.REST.delete_resource(deps.seed_model, deps.seed_id);
                        for (i = 0; i < deps.order.length; i += 1) {
                            ids = [];
                            for (j = 0; j < deps[deps.order[i]].length; j += 1) {
                                ids.push(deps[deps.order[i]][j].id);
                            }
                            MAG.REST.delete_resources(deps.order[i], ids);
                        }
                        window.location = '/citations/work/';
                    } else {
                        CIT.handle_error('delete', 401, 'cit_work');
                    }
                }});
                break;
            case 'cit_edition':
                MAG.AUTH.check_permissions({'cit_edition': ['delete'], 'cit_comcitation': ['update']}, {'success': function(response) {
                    if (response[0] === true) {
                        MAG.REST.delete_resource(deps.seed_model, deps.seed_id);
                        id_list = [];
                        for (i = 0; i < deps['cit_comcitation'].length; i += 1) {
                            id_list.push(deps['cit_comcitation'][i].id);
                        }
                        MAG.REST.update_field_selection('cit_comcitation', {'_id': {'$in': id_list}}, {'$unset':{'edition_id': 1}}, {'success': function (response) {
                            window.location = '/citations/edition/';
                        }});
                    } else {
                        CIT.handle_error('delete', 401, 'cit_edition');
                    }
                }});
                break;
            case 'cit_series':
                MAG.AUTH.check_permissions({'cit_series': ['delete'], 'cit_edition': ['update']}, {'success': function(response) {
                    if (response[0] === true) {
                        MAG.REST.delete_resource(deps.seed_model, deps.seed_id);
                        id_list = [];
                        for (i = 0; i < deps['cit_edition'].length; i += 1) {
                            id_list.push(deps['cit_edition'][i].id);
                        }
                        MAG.REST.update_field_selection('cit_edition', {'_id': {'$in': id_list}}, {'$unset':{'series_id': 1}}, {'success': function (response) {
                            window.location = '/citations/series/';
                        }});
                    } else {
                        CIT.handle_error('delete', 401, 'cit_series');
                    }
                }});
                break;
            case 'cit_onlinecorpus':
                MAG.AUTH.check_permissions({'cit_onlinecorpus': ['delete'], 'cit_edition': ['update']}, {'success': function(response) {
                    if (response[0] === true) {
                        MAG.REST.delete_resource(deps.seed_model, deps.seed_id);
                        id_list = [];
                        for (i = 0; i < deps['cit_edition'].length; i += 1) {
                            id_list.push(deps['cit_edition'][i].id);
                        }
                        MAG.REST.update_field_selection('cit_edition', {'_id': {'$in': id_list}}, {'$unset':{'onlinecorpus_id': 1}}, {'success': function (response) {
                            window.location = '/citations/onlinecorpus/';
                        }});
                    } else {
                        CIT.handle_error('delete', 401, 'cit_onlinecorpus');
                    }
                }});
                break;
            case 'cit_citation':
        	MAG.AUTH.check_permissions({'cit_citation': ['delete']}, {'success': function(response) {
        	    if (response[0] === true) {
        		MAG.REST.delete_resource(deps.seed_model, deps.seed_id);
        		window.location = '/citations/citation/';
        	    } else {
        		CIT.handle_error('delete', 401, 'cit_citation');
        	    }
        	}});
            }
        },
        
        apply_function_to_deps: function (deps, fnstring, fnargs) {
            if (MAG.TYPES.is_array(fnargs)) {
                fnargs.push(deps);
                MAG.FUNCTOOLS.get_function_from_string(fnstring).apply(this, fnargs);
            } else if (fnargs !== undefined) {
                fnargs = [fnargs];
                fnargs.push(deps);
                MAG.FUNCTOOLS.get_function_from_string(fnstring).apply(this, fnargs);
            } else {
                MAG.FUNCTOOLS.get_function_from_string(fnstring)(deps);
            }
        },
        
        do_get_dependencies: function (deps, fnstring, fnargs, i) {
            var id, criteria, j, k, key_list, object_list, display;
            if (typeof i == 'undefined') {
        	i = 0;
            }
            if (i >= deps.chain.length) {
        	CIT.apply_function_to_deps(deps, fnstring, fnargs);
        	return;
            } 
            if (i === 0) {
        	criteria = {};
        	criteria[deps.seed_model.replace(CIT.model_namespace, '') + '_id'] = {'$in' :[deps.seed_id]};
            } else {
        	criteria = {};
        	criteria[deps.chain[i-1].replace(CIT.model_namespace, '') + '_id'] = {'$in':deps[deps.chain[i-1] + '_ids']};
            }
            MAG.REST.apply_to_list_of_resources(deps.chain[i], {'criteria': criteria, 'success': function (response) {
        	key_list = [];
                object_list = [];
                if (response.results.length > 0) {
                    for (j = 0; j < response.results.length; j += 1) {
                        key_list.push(response.results[j]._id);
                        display = response.results[j]._id; //fallback
                        for (k = 0; k < deps.display_keys[i].length; k += 1) {
                            if (response.results[j].hasOwnProperty(deps.display_keys[i][k])) {
                        	display = response.results[j][deps.display_keys[i][k]];
                            }
                        }
                        object_list.push({'id': response.results[j]._id, 'display': display});
                    }
                    deps[deps.chain[i]] = object_list;
                    deps[deps.chain[i] + '_ids'] = key_list;
                    deps['order'].push(deps.chain[i]);
                }
                CIT.do_get_dependencies(deps, fnstring, fnargs, i += 1);
            }});
        },
        
        get_dependencies: function(model, id, fnstring, fnargs){
            var deps, i, key_list, object_list, works;
            deps = {};
            deps['seed_id'] = id;
            deps['seed_model'] = model;
            deps['order'] = [];
            switch (model) {
            case 'cit_author':
                deps['chain'] = ['cit_work', 'cit_edition', 'cit_comcitation'];
                deps['display_keys'] = [['abbreviation', 'title'], ['_id'], ['_id']];
                deps['primary'] = ['cit_work', 'cit_edition', 'cit_comcitation'];
                deps['secondary'] = [];
                CIT.do_get_dependencies(deps, fnstring, fnargs);
                break;
            case 'cit_work':
        	deps['chain'] = ['cit_edition', 'cit_comcitation'];
                deps['display_keys'] = [['_id'], ['_id']];
                deps['primary'] = ['cit_edition', 'cit_comcitation'];
                deps['secondary'] = [];
                CIT.do_get_dependencies(deps, fnstring, fnargs);
                break;
            case 'cit_edition':
        	deps['chain'] = ['cit_comcitation'];
                deps['display_keys'] = [['_id']];
                deps['primary'] = [];
                deps['secondary'] = ['cit_comcitation'];
                CIT.do_get_dependencies(deps, fnstring, fnargs);
                break;
            case 'cit_series':
        	deps['chain'] = ['cit_edition'];
                deps['display_keys'] = [['_id']];
                deps['primary'] = [];
                deps['secondary'] = ['cit_edition'];
                CIT.do_get_dependencies(deps, fnstring, fnargs);
                break;
            case 'cit_onlinecorpus':
        	deps['chain'] = ['cit_edition'];
                deps['display_keys'] = [['_id']];
                deps['primary'] = [];
                deps['secondary'] = ['cit_edition'];
                CIT.do_get_dependencies(deps, fnstring, fnargs);
                break;
            default:
        	deps['chain'] = [];
            	deps['display_keys'] = [];
            	deps['primary'] = [];
            	deps['secondary'] = [];
        	CIT.do_get_dependencies(deps, fnstring, fnargs);
            }
        },
        
        
        //TODO: could this be done more efficiently?
        update_identifier: function (model){
            var abbr, author_id, work_id, date, book, chapter, verse, bib_reference, exists, i;
            switch (model) {
            case 'cit_author':
                abbr = CIT.idify_string(document.getElementById('abbreviation').value);
                document.getElementById('identifier').value = abbr;
                break;
            case 'cit_work':
                author_id = document.getElementById('author_id').value;
                if (author_id === 'none') {
                    author_id = '';
                } else {
                    author_id = author_id + '_';
                }
                abbr = document.getElementById('abbreviation').value;
                document.getElementById('identifier').value = CIT.idify_string(author_id + abbr);
                break;
            case 'cit_edition':
                work_id = document.getElementById('work_id').value;
                if (work_id === 'none') {
                    work_id = '';
                } else {
                    work_id = work_id + '_';
                }
                MAG.COMMAND.get_unique_id('cit_edition', CIT.idify_string(work_id + 'edition'), {'success': function (response) {
                    document.getElementById('identifier').value = response;
                }});
                break;
            case 'cit_comcitation':
                book = document.getElementById('book').value;
                chapter = document.getElementById('chapter').value;
                verse = document.getElementById('verse').value;
                if (book !== 'none' && chapter !== '' && verse !== '') {
                    if (book.length < 2){
                        book = '0' + book;
                    }
                    if (chapter.length < 2) {
                        chapter = '0' + chapter;
                    }
                    if (verse.length < 2) {
                        verse = '0' + verse;
                    }
                    bib_reference = book + chapter + verse;
                } else {
                    bib_reference = '';
                }
                work_id = document.getElementById('work_id').value;
                if (work_id !== 'none') {

                } else {
                    work_id = '';
                }
                document.getElementById('identifier').value = CIT.idify_string(bib_reference + '_' + work_id);
                break;
            case 'cit_citation':
        	book = document.getElementById('book').value;
                chapter = document.getElementById('chapter').value;
                verse = document.getElementById('verse').value;
                if (book !== 'none' && chapter !== '' && verse !== '') {
                    if (book.length < 2){
                        book = '0' + book;
                    }
                    if (chapter.length < 2) {
                        chapter = '0' + chapter;
                    }
                    if (verse.length < 2) {
                        verse = '0' + verse;
                    }
                    bib_reference = book + chapter + verse;
                } else {
                    bib_reference = '';
                }
                work_id = document.getElementById('work_id').value;
                if (work_id !== 'none') {

                } else {
                    work_id = '';
                }
                document.getElementById('identifier').value = CIT.idify_string(bib_reference + '_' + work_id);
                break;
            }
        },

        get_biblical_ref: function(json) {
            var  book, chapter, verse;
            if (json.book.toString().length < 2) {
                book = '0' + json.book.toString();
            } else {
                book = json.book.toString();
            }
            if (json.chapter.toString().length < 2) {
                chapter = '0' + json.chapter.toString();
            } else {
                chapter = json.chapter.toString();
            }
            if (json.verse.toString().length < 2) {
                verse = '0' + json.verse.toString();
            } else {
                verse = json.verse.toString();
            }
            return book + chapter + verse;
        },


        handle_error: function (action, error_report, model) {
            var report;
            report = 'An error has occurred.<br/>';
            if (error_report.status === 401) {
                report += '<br/>You are not authorised to ' + action + ' an entry in the ' + model + ' table.';
            } else if (error_report.status === 409) {
                report += '<br/>It is not possible to ' + action + ' this ' + model + ' because an entry already exists with the same id.';
            } else if (error_report.status === 404) {
                report += '<br/>It is not possible to ' + action + ' this ' + model + ' because there is no ' + model + ' with this id.';
                report += '<br/><br/>This form can be used to add a new ' + model + '.';
            } else {
                report += '<br/>The server has encountered an error. Please try again. <br/>If the problem persists please contact the server administrator.';
            }
            CIT.show_error_box(report);
        },

        show_error_box: function (report) {
            var error_div;
            if (document.getElementById('error') !== null) {
                document.getElementsByTagName('body')[0].removeChild(document.getElementById('error'));
            }
            error_div = document.createElement('div');
            error_div.setAttribute('id', 'error');
            error_div.setAttribute('class', 'error_message');
            error_div.innerHTML = '<span id="error_title"><b>Error</b></span><div id="error_close">close</div><br/><br/>' + report;
            document.getElementsByTagName('body')[0].appendChild(error_div);
            MAG.EVENT.addEventListener(document.getElementById('error_close'), 'click', function(event){
                document.getElementsByTagName('body')[0].removeChild(document.getElementById('error'));
            });
        },

        
        check_login_status: function () {
	    var elem, query;
	    CIT.show_login_status();
	    MAG.AUTH.get_user_info({'success': function (user) {
		MENU.choose_menu_to_display(user);
	    }});
        },
        
        show_login_status: function () {
            var elem, login_status_message;
            elem = document.getElementById('login_status');
            if (elem !== null) {
                MAG.AUTH.get_user_info({'success': function(response) {
                    if (response.hasOwnProperty('ITSEE_id')) {
                        login_status_message = 'logged in as ' + response.ITSEE_id;
                    } else {
                        login_status_message = 'logged in ';
                    }
                    elem.innerHTML = login_status_message + '<br/><a href="javascript:CIT.log_user_out(\'' + window.location.href + '\')">logout</a>';

                }, 'error': function(response){
                    elem.innerHTML = '<br/><a href="javascript:MAG.AUTH.log_user_in(\'' + window.location.href + '\')">login</a>';
                }});
            }
        },
        
        log_user_out: function (next) {
            CIT._project = {};
            CIT.delete_citation_cookies();
            MAG.AUTH.log_user_out(next);
        },
       
        

/*************************************************************
 * save, submit, validate
 */
        save: function (form_id, next) {
        	var json;
        	if (form_id === 'cit_citation_form') {
        		json = CIT.CIT.custom_serialize_form(form_id);
        	} else {
        		json = MAG.FORMS.serialize_form(form_id);
        	}
        	if (json.hasOwnProperty('_id')) {
        		CIT.save_resource(json._model, json, next, 'update');
        	} else {
        		CIT.save_new_resource(json, next, 'create');
        	}
        	return;
        },
        
        /* first gets the id then calls CIT.save_resource */
        save_new_resource: function (json, next, type) {
            switch (json._model) {
            case 'cit_work': 
        	json._id = CIT.idify_string(json.author_id + '_' + (json.abbreviation || (json.title ? json.title[0] : 'none')));
        	CIT.save_resource(json._model, json, next, type);
        	break;
            case 'cit_edition':
        	MAG.COMMAND.get_unique_id('cit_edition', CIT.idify_string(json.work_id + '_edition'), {'success': function (response){
        	    json._id = response;
        	    CIT.save_resource(json._model, json, next, type);           	    
        	}});
        	break;
            case 'cit_comcitation':
        	MAG.COMMAND.get_unique_id('cit_comcitation', CIT.idify_string(CIT.get_biblical_ref(json) + '_' + json.work_id), {'success': function (response) {
        	    json._id = response;
        	    CIT.save_resource(json._model, json, next, type);  
        	}});
        	break; 
            case 'cit_citation':
        	MAG.COMMAND.get_unique_id('cit_citation', CIT.idify_string(CIT.get_biblical_ref(json) + '_' + json.work_id), {'success': function (response) {
        	    json._id = response;
        	    CIT.save_resource(json._model, json, next, type);  
        	}});
        	break;
            default:
        	json._id = CIT.idify_string(json.abbreviation);
            	CIT.save_resource(json._model, json, next, type);
            	break;
            }
        },
        
        load_next_page: function(model, id, next, bibref) {
        	var model_label, item;
        	model_label = model.replace(CIT.model_namespace, '')
            if (bibref !== undefined) {
                window.location = '/citations/' + model_label + '/edit/?' + MAG.URL.build_query_string(bibref);
            } else {
                if (next === undefined) {
                    window.location.search = model_label + '=' + id;
                } else {
                    window.location = next;
                }
            }
            //TODO: remove for loop once timestamps work
            for (item in localStorage) {
                if (item.indexOf('/api/' + model) !== -1) {
                	return localStorage.removeItem(item);
                }
            }
        },

        save_resource: function (model, json, next, type) {
            var options, bibref, item;
            bibref = undefined;
            //here get the current window and if there is a back in the keys then add them to next url
            if (model === 'cit_comcitation' || model === 'cit_citation') {
                json.biblical_reference = CIT.get_biblical_ref(json);
                if (next === 'same') {
                    bibref = {'book' : json.book, 'chapter' : json.chapter, 'verse': json.verse};
                } else if (next === 'next') {
                    bibref = {'book' : json.book, 'chapter' : json.chapter, 'verse': json.verse + 1};
                }        
            }
            if (model === 'cit_biblindex_citation') {
        	if (next === 'record') {                   
                    bibref = {'biblindex_citation': CIT.increment_biblindex_id(json._id)};                    
                }     
            }
            if (document.getElementById('save_comment') !== null && document.getElementById('save_comment').value !== '') {
                options = {'comment': document.getElementById('save_comment').value, 'success': function() {
                    CIT.load_next_page(json._model, json._id, next, bibref);
                }, 'error': function(response) {
                    CIT.handle_error('create', response, json._model);
                }};
            } else {
                options = {'success': function() {
                    CIT.load_next_page(json._model, json._id, next, bibref);
                }, 'error': function(response) {
                    CIT.handle_error('create', response, json._model);
                }};
            }
            if (type === 'create') {
                MAG.REST.create_resource(json._model, json, options);
            } else if (type === 'update') {
                MAG.REST.update_resource(json._model, json, options);
            }
        },

        validate_form: function (form_id) {
            var validation, i, alt_elems;
            validation = MAG.FORMS.validate_form(form_id);
            if (form_id === 'cit_comcitation_form') {
                alt_elems = [document.getElementById('is_ms'), document.getElementById('edition_id'), document.getElementById('ms_siglum')];
                for (i = 0; i < alt_elems.length; i += 1) {
                    MAG.EVENT.addEventListener(alt_elems[i], 'change', function(event) {
                       if (document.getElementById('is_ms').checked === true) {
                           if (document.getElementById('ms_siglum').value === '') {
                               MAG.ELEMENT.add_className(document.getElementById('ms_siglum').parentNode, 'missing');
                           } else {
                               MAG.ELEMENT.remove_className(document.getElementById('ms_siglum').parentNode, 'missing');
                           }
                           MAG.ELEMENT.remove_className(document.getElementById('edition_id').parentNode, 'missing');
                       } else {
                           if (document.getElementById('edition_id').value === 'none') {
                               MAG.ELEMENT.add_className(document.getElementById('edition_id').parentNode, 'missing');
                           } else {
                               MAG.ELEMENT.remove_className(document.getElementById('edition_id').parentNode, 'missing');
                           }
                           MAG.ELEMENT.remove_className(document.getElementById('ms_siglum').parentNode, 'missing');
                       }
                    });
                }
            }
            return validation;
        },

        validate_element: function(elem) {
            var dict;
            dict = MAG.FORMS.validate_element(elem);
            if (dict.missing === true) {
                MAG.ELEMENT.add_className(elem.parentNode, 'missing');
            } else {
                MAG.ELEMENT.remove_className(elem.parentNode, 'missing');
            }
            if (dict.invalid === true) {
                MAG.ELEMENT.add_className(elem, 'error');
            } else {
                MAG.ELEMENT.remove_className(elem, 'error');
            }
        },

        validate_elem_regex: function(elem, regex) {
            var match;
            match = regex.test(elem.value);
            if (match === false) {
                MAG.ELEMENT.add_className(elem, 'error');
            } else {
                MAG.ELEMENT.remove_className(elem, 'error');
            }
        },

        submit: function (form_id, next) {
            var validation;
            validation = CIT.validate_form(form_id);
            if (validation.result === true) {
                CIT.save(form_id, next);
            } else {
                MAG.DISPLAY.show_validation(validation);
                CIT.show_error_box('<br/>The data is not valid and cannot be saved. Please fix the errors and resave.'
                        + '<br/><br/>Red label text indicates that required data has not been supplied.'
                        + '<br/>A red background indicates that the data in that box is not in a format that is valid.');
            }
            return;
        },



/***************************************************************************
 * basic loading forms stuff
 */
        //need to recognise back here so return to page works
        //TODO: sort out error pages
        edit_data: function (model) {
        	var param_dict, bk, model_label, remembered_project, project;
        	model_label = model.replace(CIT.model_namespace, '');
        	CIT.show_loading_overlay();
        	CIT.show_login_status();
        	MAG.AUTH.get_user_info({'success': function(user) {
        		MAG.AUTH.check_permission(model, 'update', {'success': function (update_permission) { 		    
        			if (update_permission === true) {
        				//we now know they have general edit permissions for the relevant model
        				//we need to check if they are working in a project and therefore can currently edit the data
        				remembered_project = CIT.get_project_cookie('project');
        				MAG.REST.apply_to_list_of_resources('cit_project', {'criteria': {'_id': remembered_project}, 'success': function (response) {
        					if (remembered_project !== '' && remembered_project !== 'None' && response.results.length === 1) {
        						CIT._project = response.results[0];
        						param_dict = MAG.URL.get_current_query();
        						if (param_dict.hasOwnProperty(model_label)) {
        							MAG._REQUEST.request('http://' + SITE_DOMAIN + '/citations/htmlfragments/' + model + '_form.html', {
        								'mime' : 'text',
        								'success' : function (html) {
        									document.getElementById('container').innerHTML = html;
        									CIT.load_data(model, param_dict[model_label]);
        								}});
        						} else if ((model === 'cit_comcitation' || model === 'cit_citation') && param_dict.hasOwnProperty('book')) {
        							//if we are 'adding a citation of the next verse' then deal with prepopulation
        							MAG._REQUEST.request('http://' + SITE_DOMAIN + '/citations/htmlfragments/' + model + '_form.html', {
        								'mime' : 'text',
        								'success' : function (html) {
        									document.getElementById('container').innerHTML = html;
        									MAG.REST.apply_to_list_of_resources('verse', {'criteria' :
        									{'siglum': 'vg^st5', 'book_number': param_dict.book, 'chapter_number': param_dict.chapter, 'verse_number': param_dict.verse},
        									'success': function(response) {
        										var json;
        										if (response.results.length > 0) {
        											json = {'book': param_dict.book,'chapter': param_dict.chapter, 'verse': param_dict.verse};
        											MAG.FORMS.populate_simple_form(json);		                			
        											CIT.COMCIT.get_basetext(model, json);
        											CIT.update_identifier(model);
        											CIT.prepare_form(model);
        										} else {
        											json = {'book': param_dict.book,'chapter': + parseInt(param_dict.chapter) + 1, 'verse': 1};
        											MAG.FORMS.populate_simple_form(json);
        											CIT.COMCIT.get_basetext(model, json);
        											CIT.update_identifier(model);
        											CIT.prepare_form(model);
        										}
        									}});
        								}});
        						} else {
        							MAG._REQUEST.request('http://' + SITE_DOMAIN + '/citations/htmlfragments/' + model + '_form.html', {
        								'mime' : 'text',
        								'success' : function (html) {
        									document.getElementById('container').innerHTML = html;
        									CIT.prepare_form(model);
        								}});
        						}
        					} else {
        						document.getElementById('container').innerHTML = '<p>You do not have permission to edit this data.</p>'
        							+ '<p>If you are an editor for a project you need to return to the home page and select the project in order to be able to edit and add new records.</p>';
        					}
        				}});
        			} else {
        				CIT.remove_loading_overlay();
        				document.getElementById('container').innerHTML = '<p>You do not have permission to edit this data.</p>';
        				return;
        			}
        		}});
        		return;
        	}});
        },
        
        //TODO: sort out the error pages
        display_data: function (model) {
            var param_dict, elem, model_label, remembered, project, options;
            CIT.show_loading_overlay();
            CIT.show_login_status();
            model_label = model.replace(CIT.model_namespace, '');
            param_dict = MAG.URL.get_current_query();
            remembered = CIT.get_project_cookie('project');            
            //if we have the model in the params then we that points to _id in model and we are dealing with a single record
            if (param_dict.hasOwnProperty(model_label)) {
                MAG.AUTH.check_permission(model, 'read', {'success': function (read_permission) {
                    if (read_permission === true) {
                        MAG.REST.apply_to_resource(model, param_dict[model_label], {'success' : function (json) {
                            CIT.get_dependencies(model, json._id, 'CIT.show_instance_table', [json, 'content', {'blanks': true}]);
                        }});
                        document.getElementById('title').innerHTML = MAG.DISPLAY.capitalise_titles(model_label);
                        document.getElementById('breadcrumbs').innerHTML += ' &gt; <a href="/citations/' + model_label + '/">' + MAG.DISPLAY.capitalise_titles(model_label) + ' List</a>';
                        MAG.AUTH.check_permission(model, 'update', {'success': function (update_permission) {
                            if (update_permission === true) {
                                if (document.getElementById('create_link') !== null) {
                                    elem = document.getElementById('create_link');
                                    elem.setAttribute('id', 'edit_link');
                                    elem.innerHTML = '<a href="/citations/' + model_label + '/edit/?' + model_label + '=' + param_dict[model_label] + '">edit this ' + model_label + '</a>';
                                }
                            } else {
                        	document.getElementById('content').innerHTML = '<p>You do not have permission to access this data</p>';
                            }
                            CIT.remove_loading_overlay();
                        }});
                    } else {
                	document.getElementById('content').innerHTML = '<p>You do not have permission to access this data</p>';
                	CIT.remove_loading_overlay();
                    }
                }});
            //otherwise we are looking at a list
            } else {
                MAG.AUTH.check_permission(model, 'read', {'success': function (read_permission) {
                    if (read_permission === true) {
                	options = {'page_size': CIT.page_size, 'auto_sort': true, 'callback': CIT.remove_loading_overlay};
                	MAG.REST.apply_to_list_of_resources('cit_project', {'criteria': {'_id': remembered}, 'success': function (response) {
                	    if (response.results.length === 1) {
                		project = response.results[0];
                	    }
                	    if (model === 'cit_author') {
                		if (remembered === '' || remembered === 'None' || response.results.length !== 1) {
                        	    options.key_order = [{'type': 'link',
                                        'href': '/citations/author/',
                                        'text': 'view',
                                        'params': {'author': 'VAR-_id'}}, 'abbreviation', 'full_name', 'clavis', 'century_active', 'pseudonymous',
                                                {'id': 'anonymous_collective', 'label': 'Anonymous'}, {'id':'translated_source', 'label':'Translated'}, 'obsolete',];
                		} else {
                		    options.criteria = {'tradition': project.language};
                		    if (project.hasOwnProperty('author_ids')) {
                			options.criteria.abbreviation = {'$in': project.author_ids};
                		    } else {
                			MAG.AUTH.check_permission(model, 'create', {'success': function (create_permission) {
                			    if (create_permission === true) {
                				if (document.getElementById('create_link') !== null) {
                				    document.getElementById('create_link').innerHTML = '<a href="edit/">add new ' + model_label + '</a>';
                				}
                			    }
                			}});
                		    }
                		}
                	    } else if (model === 'cit_work') {
                		if (remembered === '' || remembered === 'None' || response.results.length !== 1) {
                		    options.key_order = [{'type': 'link',
                                        'href': '/citations/work/',
                                        'text': 'view',
                                        'params': {'work': 'VAR-_id'}}, 'author_id', 'abbreviation', 'title', 'clavis','obsolete'];
                		} else {
                		    options.criteria = {'language': project.language};
                		    if (project.hasOwnProperty('author_ids')) {
                			options.criteria.author_id = {'$in': project.author_ids};
                		    }
                		    MAG.AUTH.check_permission(model, 'create', {'success': function (create_permission) {
                			if (create_permission === true) {
                			    if (document.getElementById('create_link') !== null) {
                				document.getElementById('create_link').innerHTML = '<a href="edit/">add new ' + model_label + '</a>';
                			    }
                			}
                		    }});
                		}
                	    } else if (model === 'cit_edition') {
                		if (remembered === '' || remembered === 'None' || response.results.length !== 1) {
                		    options.key_order = [{'type': 'link',
                                        'href': '/citations/edition/',
                                        'text': 'view',
                                        'params': {'edition': 'VAR-_id'}}, 'work_id', 'date', 'editor', 'series_id', 'volume', 'independent_title'];
                		} else {
                		    options.criteria = {'language': project.language};
                		    if (project.hasOwnProperty('author_ids')) {
                			options.criteria.author_id = {'$in': project.author_ids};
                		    }
                		    MAG.AUTH.check_permission(model, 'create', {'success': function (create_permission) {
                			if (create_permission === true) {
                			    if (document.getElementById('create_link') !== null) {
                				document.getElementById('create_link').innerHTML = '<a href="edit/">add new ' + model_label + '</a>';
                			    }
                			}
                		    }});
                		}
                	    } else if (model === 'cit_citation') {
                		if (remembered === '' || remembered === 'None' || response.results.length !== 1) {
                		    options.key_order = [{'type': 'link',
                                        'href': '/citations/citation/',
                                        'text': 'view',
                                        'params': {'citation': 'VAR-_id'}}, {'id': 'transcription_date', 'label': 'entry date'}, {'id':'_id', 'label': 'ID'}, 
                                        	{'id': 'onlinecorpus_id', 'label': 'online corpus'}, 
                                        	'citation_text', 'citation_type'];
                		} else {
                		    options.criteria = {'language': project.language};
                		    if (project.hasOwnProperty('book_number')) {
                			options.criteria.book = project.book_number;
                		    }
                		    if (project.hasOwnProperty('author_ids')) {
                			options.criteria.author_id = {'$in': project.author_ids};
                		    }
                		    MAG.AUTH.check_permission(model, 'create', {'success': function (create_permission) {
                			if (create_permission === true) {
                			    if (document.getElementById('create_link') !== null) {
                				document.getElementById('create_link').innerHTML = '<a href="edit/">add new ' + model_label + '</a>';
                			    }
                			}
                		    }});
                		}
                	    } else if (model === 'cit_comcitation') {
                		if (remembered === '' || remembered === 'None' || response.results.length !== 1) {
                		    options.key_order = [{'type': 'link',
                                        'href': '/citations/comcitation/',
                                        'text': 'view',
                                        'params': {'comcitation': 'VAR-_id'}}, 'book', 'chapter', 'verse', {'id':'work_id', 'label': 'Work ID'}];
                		} else {
                		    options.criteria = {'language': project.language};
                		    if (project.hasOwnProperty('book_number')) {
                			options.criteria.book = project.book_number;
                		    }
                		    if (project.hasOwnProperty('author_ids')) {
                			options.criteria.author_id = {'$in': project.author_ids};
                		    }
                		    MAG.AUTH.check_permission(model, 'create', {'success': function (create_permission) {
                			if (create_permission === true) {
                			    if (document.getElementById('create_link') !== null) {
                				document.getElementById('create_link').innerHTML = '<a href="edit/">add new ' + model_label + '</a>';
                			    }
                			}
                		    }});
                		}
                	    } else if (model === 'cit_series') {
                		if (remembered === '' || remembered === 'None' || response.results.length !== 1) {
                		    options.key_order = [{'type': 'link',
                                        'href': '/citations/series/',
                                        'text': 'view',
                                        'params': {'series': 'VAR-_id'}}, 'abbreviation', 'title'];
                		} else {
                		    options.criteria = {'language': project.language};
                		    MAG.AUTH.check_permission(model, 'create', {'success': function (create_permission) {
                			if (create_permission === true) {
                			    if (document.getElementById('create_link') !== null) {
                				document.getElementById('create_link').innerHTML = '<a href="edit/">add new ' + model_label + '</a>';
                			    }
                			}
                		    }});
                		}
                	    } else if (model === 'cit_onlinecorpus') {
                		if (remembered === '' || remembered === 'None' || response.results.length !== 1) {
                		    options.key_order = [{'type': 'link',
                                        'href': '/citations/onlinecorpus/',
                                        'text': 'view',
                                        'params': {'onlinecorpus': 'VAR-_id'}}, 'abbreviation', 'title', 'url'];
                		} else {
                		    options.criteria = {'language': project.language};
                		    MAG.AUTH.check_permission(model, 'create', {'success': function (create_permission) {
                			if (create_permission === true) {
                			    if (document.getElementById('create_link') !== null) {
                				document.getElementById('create_link').innerHTML = '<a href="edit/">add new ' + model_label + '</a>';
                			    }
                			}
                		    }});
                		}
                	    } else if (model === 'cit_biblindex_citation') {
                		if (remembered === '' || remembered === 'None' || response.results.length !== 1) {
                		    options.key_order = [{'type': 'link',
                                        'href': '/citations/biblindex_citation/',
                                        'text': 'view',
                                        'params': {'biblindex_citation': 'VAR-_id'}}, {'id': '_id', 'label': 'ID'},
                                        {'id': 'AUCT', 'label': 'Author'}, {'id': 'ChapterValidity_ChapterNum', 'label': 'Chapter'},  {'id': 'VerseValidity_VerseNumber_start', 'label': 'Start verse'}, {'id': 'VerseValidity_VerseNumber_end', 'label': 'End verse'}, 'citation_text'];
                		} else {
                		    options.criteria = {'language': project.language};
                		    if (project.hasOwnProperty('book_string')) {
                			options.criteria.BookLabel_Abbreviation = project.book_string;
                		    }
//                		    MAG.AUTH.check_permission(model, 'create', {'success': function (create_permission) {
//                			if (create_permission === true) {
//                			    if (document.getElementById('create_link') !== null) {
//                				document.getElementById('create_link').innerHTML = '<a href="edit/">add new ' + model_label + '</a>';
//                			    }
//                			}
//                		    }});
                		}
                	    }
                	    MAG.DISPLAY.show_instance_list_table(model, 'content', options);
                	    if (typeof project !== 'undefined') {
                		document.getElementById('project_name').innerHTML = project.name;
                	    }
                	    if (document.getElementById('obsolete_check') !== null) {
                		document.getElementById('obsolete_check').innerHTML = '<label id="show_obsolete">Show Obsolete: <input id="obsolete_checkbox" name="obsolete_checkbox" type="checkbox"/></label>';
                		MAG.EVENT.addEventListener(document.getElementById('obsolete_checkbox'), 'click', function () {
                		    CIT.toggle_obsolete();
                		});
                	    }
                	}});
                    }
               }});
            }
        },

        toggle_obsolete: function () {
            var elem, query, qdict;
            elem = document.getElementById('obsolete_checkbox');
            if (elem.checked === true) {
                query = MAG.DISPLAY.create_new_query({'page': 1});
                qdict = MAG.URL.parse_query_string(query);
                delete qdict.obsolete;
                document.location.search = '?' + MAG.DISPLAY.create_new_query(qdict);
            } else {
                document.location.search = '?' + MAG.DISPLAY.create_new_query({'obsolete': {'$exists': false}, 'page': 1});
            }
        },
        
        set_form: function (model) {
        	var status_level, i, sections;
        	status_level = CIT.get_project_cookie('status');
        	if (CIT._project.hasOwnProperty('form_settings') 
        			&& CIT._project.form_settings.hasOwnProperty(model)
        			&& CIT._project.form_settings[model].hasOwnProperty(status_level)) {
        		sections = document.getElementsByClassName('form_section');
        		for (i = 0; i < sections.length; i += 1) {
        			if (CIT._project.form_settings[model][status_level].indexOf(sections[i].id) === -1) {
        				document.getElementById(sections[i].id).style.display = 'none';
        			}
        		}
        		return;
        	}
        },
        
        set_submit: function (model) {
            var status_level, i, buttons;
            status_level = CIT.get_project_cookie('status');
            if (CIT._project.hasOwnProperty('submit_settings') 
    		&& CIT._project.form_settings.hasOwnProperty(model)
    		&& CIT._project.form_settings[model].hasOwnProperty(status_level)) {
        	    buttons = document.getElementById('submit_section').getElementsByTagName('input');
        	    for (i = 0; i < buttons.length; i += 1) {
        		if (CIT._project.submit_settings[model][status_level].indexOf(buttons[i].id) === -1) {
        		    document.getElementById(buttons[i].id).style.display = 'none';
        		}
        	    }
        	    return;
            }
        },
        
        set_preselects: function (model) {
        	var key, input_hidden;
        	//I think it is okay to modify the saved project setting themselves 
        	//rather than a copy since each page is a genuine reload not ajax 
        	//so they are only kept for the current page
        	if (!CIT._project.hasOwnProperty('preselects')){
        		CIT._project.preselects = {};
        	}
        	if (!CIT._project.preselects.hasOwnProperty(model)) {
        		CIT._project.preselects[model] = {};
        	}
        	if (model === 'cit_author') {
        		if (!CIT._project.preselects[model].hasOwnProperty('language') && CIT._project.hasOwnProperty('language')) {
        			CIT._project.preselects[model].tradition = CIT._project.language;
        		}
        	} else if (model === 'cit_work') {
        		if (!CIT._project.preselects[model].hasOwnProperty('language') && CIT._project.hasOwnProperty('language')) {
        			CIT._project.preselects[model].language = CIT._project.language;
        		}
        		if (CIT._project.hasOwnProperty('author_ids') 
        				&& CIT._project.author_ids.length === 1 
        				&& !CIT._project.preselects[model].hasOwnProperty('author_id')) {
        			CIT._project.preselects[model].author_id = CIT._project.author_ids[0];
        		}
        	} else if (model === 'cit_citation') {
        		if (!CIT._project.preselects[model].hasOwnProperty('language') && CIT._project.hasOwnProperty('language')) {
        			CIT._project.preselects[model].language = CIT._project.language;
        		}
        		if (!CIT._project.preselects[model].hasOwnProperty('book') && CIT._project.hasOwnProperty('book_number')) {
        			CIT._project.preselects[model].book = CIT._project.book_number;
        		}
        		if (CIT._project.hasOwnProperty('author_ids') 
        				&& CIT._project.author_ids.length === 1 
        				&& !CIT._project.preselects[model].hasOwnProperty('author_id')) {
        			CIT._project.preselects[model].author_id = CIT._project.author_ids[0];
        		}
        	}        
        	for (key in CIT._project.preselects[model]) {
        		if (CIT._project.preselects[model].hasOwnProperty(key)) {
        			if (document.getElementById(key)) {
        				document.getElementById(key).value = CIT._project.preselects[model][key];        		
        				document.getElementById(key).disabled = 'disabled';
        				input_hidden = document.createElement('input');
        				input_hidden.setAttribute('type', 'hidden');
        				input_hidden.setAttribute('name', key);
        				input_hidden.setAttribute('value', CIT._project.preselects[model][key]);
        				if (MAG.ELEMENT.has_className(document.getElementById(key), 'integer')) {
        					MAG.ELEMENT.add_className(input_hidden, 'integer');
        				}
        				document.getElementById(model + '_form').appendChild(input_hidden);
        			}
        		}
        	}
        },
        
        set_disabled: function (json, fields) {
        	var i, input_hidden, key;
        	if (CIT._project.hasOwnProperty('preselects') && CIT._project.preselects.hasOwnProperty(json._model)) {
        		for (key in  CIT._project.preselects[json._model]) {
        			if (fields.indexOf(key) === -1) {
        				fields.push(key);
        			}
        		}
        	}
        	for (i = 0; i < fields.length; i += 1) {
        		if (document.getElementById(fields[i])) {
        			input_hidden = document.createElement('input');
        			input_hidden.setAttribute('type', 'hidden');
        			input_hidden.setAttribute('name', fields[i]);
        			input_hidden.setAttribute('id', fields[i] + '_hidden')
        			if (json.hasOwnProperty(fields[i])) {
        				input_hidden.setAttribute('value', json[fields[i]]);
        			} else {
        				input_hidden.setAttribute('value', '');
        			}
        			if (MAG.ELEMENT.has_className(document.getElementById(fields[i]), 'integer')) {
        				MAG.ELEMENT.add_className(input_hidden, 'integer');
        			}
        			document.getElementById(json._model + '_form').appendChild(input_hidden);
        			document.getElementById(fields[i]).disabled = 'disabled';
        		}
        	}
        },
        
        //TODO: this and project settings should be able to accommodate a range of books not just one or everything
        populate_book: function (model, options) {
            var book;
            if (typeof options === 'undefined') {
        	options = {};
            }
            if (options.hasOwnProperty('select')) {
        	book = options.select;
            }
            if (typeof book === 'undefined' && CIT._project.hasOwnProperty('book_number')) {
        	book = CIT._project.book_number;
            }
            //TODO: add in a preselects check
            MAG.REST.apply_to_list_of_resources('work', {'criteria': {'_sort':[['book_number', 1]]}, 'success': function (response) {
        	MAG.FORMS.populate_select(response.results, document.getElementById('book'), 'book_number', 'name', book);
            }});
            
        },
        
        //populate an author drop down following the constraints of the current project
        //if author supplied or certain criteria are met an author is also preselected
        //provide model for checking any defined preselects
        //options 'select' = string - the value to preselect
        //	'inc_obsolete' = boolean - include records marked obsolete default is to include them
        populate_author: function (model, options) {
        	var criteria, author;
        	if (typeof options === 'undefined') {
        		options = {};
        	}
        	if (options.hasOwnProperty('select')) {
        		author = options.select;
        	}
        	criteria = {'_sort':[['abbreviation', 1]], 'tradition': CIT._project.language};
        	if (options.hasOwnProperty('inc_obsolete') && options.inc_obsolete === false) {
        		criteria.obsolete = {'$exists': false};
        	}
        	if (CIT._project.hasOwnProperty('author_ids')) {
        		criteria._id = {'$in': CIT._project.author_ids};
        		if (CIT._project.author_ids.length === 1 && typeof author === 'undefined') {
        			author = CIT._project.author_ids[0];
        		}
        	}
        	//if we still don't have an author preselected then check project preselect settings
        	if (typeof author === 'undefined' 
        		&& CIT._project.hasOwnProperty('preselects') 
        		&& CIT._project.preselects.hasOwnProperty(model) 
        		&& CIT._project.preselects[model].hasOwnProperty('author_id')) {
        		author = CIT._project.preselects[model].author_id;
        	}
        	MAG.REST.apply_to_list_of_resources('cit_author', {'criteria': criteria, 'success': function (response) {
        		CIT.populate_select_with_obsolete(response.results, document.getElementById('author_id'), '_id', {1 : 'abbreviation', 2 : 'full_name'}, author);
        	}});
        },
        
        //populate a work drop down following the constraints of the current project
        //'select' = string - the value to preselect
        //	'inc_obsolete' = boolean - include records marked obsolete default is to include them
        //	'author' - string - contrain results by specified author 
        populate_work: function (model, options) {
        	var criteria, work, reenable;
        	reenable = false;
        	if (typeof options === 'undefined') {
        		options = {};
        	}
        	if (options.hasOwnProperty('select')) {
        		work = options.select;
        	} else {
        		work = 'none';
        	}
        	criteria = {'_sort':[['abbreviation', 1]], 'language': CIT._project.language};
        	if (options.hasOwnProperty('inc_obsolete') && options.inc_obsolete === false) {
        		criteria.obsolete = {'$exists': false};
        	}
        	if (options.hasOwnProperty('author')) {
        		criteria.author_id = options.author;
        	} else if (CIT._project.hasOwnProperty('author_ids')) {
        		criteria.author_id = {'$in': CIT._project.author_ids};
        	}
        	if (work === 'none' 
        		&& CIT._project.hasOwnProperty('preselects') 
        		&& CIT._project.preselects.hasOwnProperty(model) 
        		&& CIT._project.preselects[model].hasOwnProperty('work_id')) {
        		work = CIT._project.preselects[model].work_id;
        	}
        	if (criteria.hasOwnProperty('author_id') && work === 'none') {
        		reenable = true;
        	}
        	MAG.REST.apply_to_list_of_resources('cit_work', {'criteria' : criteria, 'success' : function (response) {
        		CIT.populate_select_with_obsolete(response.results, document.getElementById('work_id'), '_id', {1 : 'abbreviation', 2 : 'title'},  work, reenable);

        	}});
        },
        
        //options - select - string - the value to select          
        populate_onlinecorpus: function (model, options) {
            var criteria, onlinecorpus;
            if (typeof options === 'undefined') {
        	options = {};
            }
            if (options.hasOwnProperty('select')) {
        	onlinecorpus = options.select;
            } else {
        	onlinecorpus = 'none';
            }
            criteria = {'_sort':[['abbreviation', 1]], 'language': CIT._project.language};
            if (onlinecorpus === 'none' 
			&& CIT._project.hasOwnProperty('preselects') 
			&& CIT._project.preselects.hasOwnProperty(model) 
			&& CIT._project.preselects[model].hasOwnProperty('onlinecorpus_id')) {
        	onlinecorpus = CIT._project.preselects[model].onlinecorpus_id;
            }
            MAG.REST.apply_to_list_of_resources('cit_onlinecorpus', {'success' : function (response) {
                MAG.FORMS.populate_select(response.results, document.getElementById('onlinecorpus_id'), '_id', 'abbreviation', onlinecorpus);
            }});
        },
        

        load_data: function (model, id) {
            var author, work, series, edition, onlinecorpus, text, history, book_hidden, verse_hidden,
            	chapter_hidden, date, bk, model_label, criteria, i, key, parent, html, book, lookup_json;
            model_label = model.replace(CIT.model_namespace, '');
            CIT.show_login_status();
            document.getElementById('page_title').innerHTML = MAG.DISPLAY.capitalise_titles(model_label) + ' Data Entry Form';
            document.getElementById('breadcrumbs').innerHTML += ' &gt; <a href="/citations/' + model_label + '/">' + MAG.DISPLAY.capitalise_titles(model_label) + ' List</a>';
            switch (model) {
            case 'cit_author':
            	document.getElementById('project_name').innerHTML = CIT._project.name;
            	criteria = {'tradition': CIT._project.language};
            	if (CIT._project.hasOwnProperty('author_ids')) {
            	    criteria['$and'] = [{'_id': id}, {'_id': {'$in': CIT._project.author_ids}}]; //this ensures the project permissions regarding author are respected
            	} else {
            	    criteria._id = id;
            	}
            	MAG.REST.apply_to_list_of_resources('cit_author', {'criteria': criteria, 'success': function (response) {
            		if (response.results.length === 1) {
            			//this is the bit that actually loads data into the form and we need for new version
            			MAG.FORMS.populate_simple_form(response.results[0], document.getElementById(model + '_form'));
            			document.getElementById('identifier').value = response.results[0]._id;
            			CIT.set_disabled(response.results[0], ['abbreviation', 'tradition']);
            			CIT.set_form(model);
            			CIT.set_submit(model);
            			CIT.add_eventHandlers(model); 
            		} else {
            			document.getElementById('container').innerHTML = '<p>You do not have permission to edit this data in this project.</p>'
            				+ '<p>To switch projects return to the homepage.</p>';
            		}
            	    CIT.remove_loading_overlay();
            	}});             	
                break;
            case 'cit_work':
        	document.getElementById('project_name').innerHTML = CIT._project.name;
        	criteria = {'language': CIT._project.language, '_id': id};
        	if (CIT._project.hasOwnProperty('author_ids')) {
        	    criteria['author_id'] = {'$in': CIT._project.author_ids}
        	}
        	MAG.REST.apply_to_list_of_resources('cit_work', {'criteria': criteria, 'success': function (response){
        		if (response.results.length === 1) {
        			author = response.results[0].author_id;
        			CIT.populate_author(model, {'select': author});
        			MAG.FORMS.populate_simple_form(response.results[0], document.getElementById(model + '_form'));
        			document.getElementById('identifier').value = response.results[0]._id;
        			CIT.set_disabled(response.results[0], ['author_id', 'language', 'abbreviation']);
        			CIT.set_form(model);
        			CIT.set_submit(model);
        			CIT.add_eventHandlers(model);
        		} else {
        			document.getElementById('container').innerHTML = '<p>You do not have permission to edit this data in this project.</p>'
        				+ '<p>To switch projects return to the homepage.</p>';
        		}
        		CIT.remove_loading_overlay();
        	}});               
                break;
            case 'cit_edition':
        	document.getElementById('project_name').innerHTML = CIT._project.name;
        	criteria = {'language': CIT._project.language, '_id': id};
        	if (CIT._project.hasOwnProperty('author_ids')) {
        	    criteria['author_id'] = {'$in': CIT._project.author_ids};
        	}
        	MAG.REST.apply_to_list_of_resources('cit_edition', {'criteria': criteria, 'success': function (response) {
        	    if (response.results.length === 1) {
        		work = response.results[0].work_id;
        		author = response.results[0].author_id;
        		series = response.results[0].series || 'none';
        		onlinecorpus = response.results[0].onlinecorpus || 'none';
        		CIT.populate_author(model, {'select': author});
        		CIT.populate_work(model, {'select': work, 'author': author})
                        MAG.REST.apply_to_list_of_resources('cit_series', {'success' : function (serieses) {
                            MAG.FORMS.populate_select(serieses.results, document.getElementById('series_id'), '_id', 'abbreviation',  series);
                        }});
        		CIT.populate_onlinecorpus(model, {'select': onlinecorpus});
                        //show legacy data
                        if (response.results[0].hasOwnProperty('legacy_edition')) {
                            document.getElementById('legacy_edition_div').style.display = 'block';
                        } 
                        MAG.FORMS.populate_simple_form(response.results[0], document.getElementById(model + '_form'));
                        document.getElementById('identifier').value = response.results[0]._id;
                        CIT.set_disabled(response.results[0], ['author_id', 'work_id', 'legacy_edition', 'language']);
                        CIT.set_form(model);
                        CIT.set_submit(model);
                        CIT.add_eventHandlers(model);
        	    } else {
        		document.getElementById('container').innerHTML = '<p>You do not have permission to edit this data in this project.</p>'
				+ '<p>To switch projects return to the homepage.</p>';
        	    }
        	    CIT.remove_loading_overlay();
                }});
                break;
            case 'cit_citation' : 
            	document.getElementById('project_name').innerHTML = CIT._project.name;
            	criteria = {'language': CIT._project.language, '_id': id};
            	if (CIT._project.hasOwnProperty('author_ids')) {
            		criteria['author_id'] = {'$in': CIT._project.author_ids};
            	}
            	if (CIT._project.hasOwnProperty('book_number')) {
            		criteria['book'] = CIT._project.book_number;
            	}
            	MAG.REST.apply_to_list_of_resources('cit_citation', {'criteria': criteria, 'success' : function (response) {
            		if (response.results.length === 1) {
            			//disable the work select until we have an author (because selecting the right work is too difficult)
            			document.getElementById('work_id').disabled = true;
            			book = response.results[0].book;
            			author = response.results[0].author_id;
            			work = response.results[0].work_id;
            			edition = response.results[0].edition_id || 'none';
            			onlinecorpus = response.results[0].onlinecorpus_id || 'none';
            			document.getElementById('identifier').value = response.results[0]._id;
            			CIT.populate_book(model, {'select': book});
            			CIT.populate_author(model, {'select': author, 'inc_obsolete': false});
            			CIT.populate_work(model, {'select': work, 'inc_obsolete': false, 'author': author});
            			CIT.CIT.prepare_edition_entry(response.results[0]);
            			CIT.populate_onlinecorpus(model, {'select': onlinecorpus});
            			//populate specific form fields for references
            			MAG.REST.apply_to_list_of_resources('work', {'criteria': {'_sort': [['short_identifier', 1]]}, 'success' : function (books) {
            				MAG.FORMS.populate_select(books.results, document.getElementById('book_catena'), 'name', 'name');
            				MAG.FORMS.populate_select(books.results, document.getElementById('book_parallel'), 'name', 'name');
            			}});
            			CIT.COMCIT.get_basetext(model, response.results[0]);
            			//show legacy data fields if required
            			if (response.results[0].hasOwnProperty('manuscript_info')) {
            				document.getElementById('manuscript_info_div').style.display = 'block';
            			}
            			if (response.results[0].hasOwnProperty('dependencies_string')) {
            				document.getElementById('dependencies_string_div').style.display = 'block';
            			}
            			//manually populate the non-form fields data
            			if (response.results[0].hasOwnProperty('biblical_catena')) {
            				for (i = 0; i < response.results[0].biblical_catena.length; i += 1) {
            					CIT.CIT.add_catena(response.results[0].biblical_catena[i])
            				}
            			}
            			if (response.results[0].hasOwnProperty('biblical_parallels')) {
            				for (i = 0; i < response.results[0].biblical_parallels.length; i += 1) {
            					CIT.CIT.add_parallel(response.results[0].biblical_parallels[i])
            				}
            			}
            			if (response.results[0].hasOwnProperty('status')) {
            				document.getElementById('status').value = response.results[0].status;
            				document.getElementById('status_value').innerHTML = response.results[0].status;
            				if (response.results[0].status.indexOf('but flagged') !== -1) {
            					document.getElementById('flag').value = 'Unflag';
            				} else {
            					document.getElementById('flag').value = 'Flag for attention';
            				}


            			}
            			//populate the rest of the form
            			MAG.FORMS.populate_complex_form(response.results[0], document.getElementById(model + '_form'), 'CIT.CIT');
            			if (response.results[0].hasOwnProperty('transcription_date')) {
            				date = new Date(response.results[0].transcription_date.$date);
            				document.getElementById('transcription_date').value = date.getTime();
            				document.getElementById('transcription_date_display').value = date.getDate() + '/' + (date.getMonth() + 1) + '/' + date.getFullYear();
            			}
            			//if there is a reviser field display details - this is for legacy data - after the first save in the new system this will come from last modified field in meta data
            			if (response.results[0].hasOwnProperty('reviser')) {
            				date = new Date(response.results[0].revision_date.$date);
            				document.getElementById('last_modified_date_display').value = date.getDate() + '/' + (date.getMonth() + 1) + '/' + date.getFullYear();
            				document.getElementById('last_edited_by_display').value = response.results[0].reviser;
            				document.getElementById('modifier_details').style.display = 'block';
            			} else if (response.results[0]._meta.hasOwnProperty('_last_modified_time')
            					&& response.results[0]._meta._last_modified_time !== 'unknown') {                     
            				date = new Date(response.results[0]._meta._last_modified_time.$date);
            				document.getElementById('last_modified_date_display').value = date.getDate() + '/' + (date.getMonth() + 1) + '/' + date.getFullYear();
            				document.getElementById('last_edited_by_display').value = response.results[0]._meta._last_modified_by_display;
            				document.getElementById('modifier_details').style.display = 'block';
            			}
            			//make sure we have at least one of each visible
            			if (!response.results[0].hasOwnProperty('manuscript_variants')) {
            				CIT.CIT.add_manuscript_variants();
            			}
            			if (!response.results[0].hasOwnProperty('dependencies')) {
            				CIT.CIT.add_dependencies();
            			}
            			CIT.set_disabled(response.results[0], ['book', 'chapter', 'verse', 'language', 'author_id', 'work_id']);
            			CIT.set_form(model);
            			CIT.set_submit(model);
            			CIT.add_eventHandlers(model);
            		} else {
            			document.getElementById('container').innerHTML = '<p>You do not have permission to edit this data in this project.</p>'
            				+ '<p>To switch projects return to the homepage.</p>';
            		}
            		CIT.remove_loading_overlay();
            	}});
            	break;
            case 'cit_comcitation':
        	document.getElementById('project_name').innerHTML = CIT._project.name;
            	criteria = {'language': CIT._project.language, '_id': id};
            	if (CIT._project.hasOwnProperty('author_ids')) {
        	    criteria['author_id'] = {'$in': CIT._project.author_ids};
        	}
            	if (CIT._project.hasOwnProperty('book_number')) {
        	    criteria['book'] = CIT._project.book_number;
        	}
            	MAG.REST.apply_to_list_of_resources('cit_comcitation', {'criteria': criteria, 'success' : function (response) {
            	    if (response.results.length === 1) {
            		author = response.results[0].author_id;
            		work = response.results[0].work_id;
            		edition = response.results[0].edition_id || 'none';
            		document.getElementById('identifier').value = response.results[0]._id;
            		CIT.populate_author(model, {'select': author, 'inc_obsolete': false});
            		CIT.populate_work(model, {'select': work, 'inc_obsolete': false, 'author': author});
                        MAG.REST.apply_to_list_of_resources('cit_edition', {'criteria' : {'_sort':[['_id', 1]], 'work_id': work}, 'success' : function (editions) {
                            MAG.FORMS.populate_select(editions.results, document.getElementById('edition_id'), '_id', '_id',  edition);
                        }});
                        CIT.COMCIT.get_basetext(model, response.results[0]);
                        MAG.FORMS.populate_complex_form(response.results[0], document.getElementById(model + '_form'), 'CIT.COMCIT');
                        if (response.hasOwnProperty('ms_siglum')) {
                            document.getElementById('ms_siglum').disabled = false;
                            document.getElementById('is_ms').checked = true;
                        }
                        if (response.hasOwnProperty('exegesis_text')) {
                            document.getElementById('exegesis_text').disabled = false;
                            document.getElementById('reconstruction_checkbox').checked = true;
                        } else {
                            document.getElementById('exegesis_text').value = response.results[0].lemma.text;
                        }
                        if (response.results[0].hasOwnProperty('lemma')) {
                            if (response.results[0].lemma.hasOwnProperty('text')) {
                        	document.getElementById('lemma_text_reminder').innerHTML = response.results[0].lemma.text;
                            }
                        }
                        if (response.results[0].hasOwnProperty('transcription_date')) {
                            date = new Date(response.results[0].transcription_date.$date);
                            document.getElementById('transcription_date').value = date.getTime();
                            document.getElementById('transcription_date_display').value = date.getDate() + '/' + (date.getMonth()+1) + '/' + date.getFullYear();
                        }
                        history = document.getElementById('history_section');
                        if (history !== null) {
                            history.innerHTML = '<br/><input type="button" class="width_half" id="history_button" value="Show history"/><div id="history" name="history"></div>';
                        }
                        if (response.results[0].status.indexOf('but flagged') !== -1) {
                            document.getElementById('flag').value = 'Unflag';
                        //MARKER
                        }
                        CIT.set_disabled(response.results[0], ['book', 'chapter', 'verse', 'language', 'author_id', 'work_id']);
                        CIT.set_form(model);
                        CIT.set_submit(model);
                        CIT.add_eventHandlers(model);
            	    } else {
            		document.getElementById('container').innerHTML = '<p>You do not have permission to edit this data in this project.</p>'
				+ '<p>To switch projects return to the homepage.</p>';
        	    }
            	    CIT.remove_loading_overlay();
                }});
                break;
            case 'cit_biblindex_citation':
        	document.getElementById('project_name').innerHTML = CIT._project.name;
        	criteria = {'language': CIT._project.language, '_id': id};
            	if (CIT._project.hasOwnProperty('book_string')) {
        	    criteria['BookLabel_Abbreviation'] = CIT._project.book_string;
        	}
            	MAG.REST.apply_to_list_of_resources('cit_biblindex_citation', {'criteria': criteria, 'success' : function (response) {
            	    if (response.results.length === 1) {
            		book = response.results[0].book_string;
            		CIT.populate_book(model, {'select': book});
            		lookup_json = {'siglum': 'TR', 
    				'_sort': [['verse_number', 1]],
    				'book_number': response.results[0].book_number, 
    				'chapter_number': response.results[0]['ChapterValidity_ChapterNum'], 
    				'verse_number': {'$gt': response.results[0]['VerseValidity_VerseNumber_start']-1, 
    				    '$lt': response.results[0]['VerseValidity_VerseNumber_end']+1}};
            		MAG.REST.apply_to_list_of_resources('verse', {'criteria': lookup_json, 'success': function (verses) {
            		    var bib_text = [];
            		    for (i = 0; i < verses.results.length; i += 1) {
            			bib_text.push(CIT.COMCIT.strip_tags(verses.results[i].tei));
            		    }
            		    document.getElementById('basetext_text').innerHTML = bib_text.join('<br/>');
            		    document.getElementById('basetext_label').innerHTML = 'TR text:';
            		}});
            		document.getElementById('identifier').value = response.results[0]['_id'];
            		document.getElementById('chapter').value = response.results[0]['ChapterValidity_ChapterNum'];
            		document.getElementById('verse_start').value = response.results[0]['VerseValidity_VerseNumber_start'];
            		document.getElementById('verse_end').value = response.results[0]['VerseValidity_VerseNumber_end'];
            		document.getElementById('lang').value = response.results[0]['language'];
            		document.getElementById('author_id').value = response.results[0]['AUCT'];
            		document.getElementById('work_id').value = response.results[0]['OPUS'];
            		document.getElementById('clavis').value = response.results[0]['CLAV'];
            		document.getElementById('work_reference').value = [response.results[0]['TX_LIB_PAT'], response.results[0]['TX_CHA_PAT'], response.results[0]['TX_PAR_PAT']].join(' ');
            		document.getElementById('page_reference').value = [response.results[0]['TX_PAG_PAT'], response.results[0]['TX_SUBPAG_PAT']].join(' ');
            		document.getElementById('line_reference').value = response.results[0]['TX_LIG_PAT'];
            		if (response.results[0].hasOwnProperty('transcription_date')) {
                            date = new Date(response.results[0].transcription_date.$date);
                            document.getElementById('transcription_date').value = date.getTime();
                            document.getElementById('transcription_date_display').value = date.getDate() + '/' + (date.getMonth() + 1) + '/' + date.getFullYear();
                            document.getElementById('transcriber').value = response.results[0].transcriber;
                            document.getElementById('transcriber_display').value = response.results[0].transcriber;
            		} else {
                            CIT.populate_transcriber();
                        }
            		MAG.EVENT.add_event(document.getElementById('corrections_required'), 'change', function () {
            		    if (document.getElementById('corrections_required').checked) {
            			document.getElementById('correction_notes').removeAttribute('disabled');
            		    } else {
            			document.getElementById('correction_notes').setAttribute('disabled', 'disabled');
            		    }
            		});
            		
            		document.getElementById('previous').href = '/citations/biblindex_citation/edit/?biblindex_citation=' + CIT.decrement_biblindex_id(response.results[0]['_id']);
            		document.getElementById('next').href = '/citations/biblindex_citation/edit/?biblindex_citation=' + CIT.increment_biblindex_id(response.results[0]['_id']);
            	    } else {
            		document.getElementById('container').innerHTML = '<p>You do not have permission to edit this data in this project.</p>'
    				+ '<p>To switch projects return to the homepage.</p>';
        	    }
            	    CIT.remove_loading_overlay();
            	}});
            default :
        	//default is not constrained by project settings - is this okay?
        	document.getElementById('project_name').innerHTML = CIT._project.name;
                MAG.REST.apply_to_resource(model, id, {'success' : function (response) {
                    MAG.FORMS.populate_simple_form(response, document.getElementById(model + '_form'));
                }});
            	CIT.set_form(model);
            	CIT.set_submit(model);
                CIT.add_eventHandlers(model);
                CIT.remove_loading_overlay();
            }
            return;
        },
        
        increment_biblindex_id: function (id) {
            var book, number;
            book = id.substring(0, id.indexOf('_'));
            number = parseInt(id.substring(id.indexOf('_')+1));
            number = number + 1;
            return book + '_' + ("000000" + number).slice(-6)
        },
        
        decrement_biblindex_id: function (id) {
            var book, number;
            book = id.substring(0, id.indexOf('_'));
            number = parseInt(id.substring(id.indexOf('_')+1));
            number = number - 1;
            return book + '_' + ("000000" + number).slice(-6)
        },

        prepare_form: function (model) {
        	var date, language, ids, i, model_label, key, input_hidden, criteria, selected, html;
        	model_label = model.replace(CIT.model_namespace, '');
        	CIT.show_login_status();
        	document.getElementById('page_title').innerHTML = MAG.DISPLAY.capitalise_titles(model_label) + ' Data Entry Form';
        	document.getElementById('breadcrumbs').innerHTML += ' &gt; <a href="/citations/' + model_label + '/">' + MAG.DISPLAY.capitalise_titles(model_label) + ' List</a>';
        	switch (model) {
        	case 'cit_work' :
        		document.getElementById('project_name').innerHTML = CIT._project.name;
        		CIT.populate_author(model);
        		CIT.set_preselects(model);
        		CIT.set_form(model);
        		CIT.set_submit(model);
        		CIT.add_eventHandlers(model);
        		CIT.add_newRecordEventHandlers(model);
        		CIT.remove_loading_overlay();
        		break;
        	case 'cit_edition' :
        		document.getElementById('project_name').innerHTML = CIT._project.name;
        		CIT.populate_author(model);
        		CIT.populate_work(model)
        		MAG.REST.apply_to_list_of_resources('cit_series', {'criteria': {'_sort':[['abbreviation', 1]]}, 'success' : function (response) {
        			MAG.FORMS.populate_select(response.results, document.getElementById('series_id'), '_id', 'abbreviation');
        		}});
        		CIT.populate_onlinecorpus(model);
        		CIT.set_preselects(model);
        		CIT.set_form(model);
        		CIT.set_submit(model);
        		CIT.add_eventHandlers(model);
        		CIT.add_newRecordEventHandlers(model);
        		CIT.remove_loading_overlay();
        		break;
        	case 'cit_citation' :        	
        		document.getElementById('project_name').innerHTML = CIT._project.name;
        		//disable the work select until we have an author (because selecting the right work is too difficult)
        		document.getElementById('work_id').disabled = true;
        		CIT.populate_book(model);
        		CIT.populate_author(model, {'inc_obsolete': false});
        		//don't need to do this anymore
        		//CIT.populate_work(model, {'inc_obsolete': false});
        		CIT.populate_onlinecorpus(model);
        		CIT.populate_transcriber();
        		CIT.CIT.prepare_edition_entry();
        		MAG.REST.apply_to_list_of_resources('work', {'criteria': {'_sort': [['short_identifier', 1]]}, 'success' : function (response) {
        			MAG.FORMS.populate_select(response.results, document.getElementById('book_catena'), 'name', 'name');
        			MAG.FORMS.populate_select(response.results, document.getElementById('book_parallel'), 'name', 'name');
        		}});
        		CIT.CIT.add_manuscript_variants();
        		CIT.CIT.add_dependencies();             
        		CIT.set_preselects(model);
        		CIT.set_form(model);
        		CIT.set_submit(model);     
        		CIT.add_eventHandlers(model);
        		CIT.add_newRecordEventHandlers(model);
        		CIT.remove_loading_overlay();
        		break;
        	case 'cit_comcitation' :       	
        		document.getElementById('project_name').innerHTML = CIT._project.name;
        		CIT.populate_author(model, {'inc_obsolete': false});
        		CIT.populate_work(model, {'inc_obsolete': false});
        		MAG.REST.apply_to_list_of_resources('cit_edition', {'criteria' : {'_sort':[['_id', 1]]}, 'success' : function (response) {
        			MAG.FORMS.populate_select(response.results, document.getElementById('edition_id'), '_id', '_id');
        		}});
        		CIT.populate_transcriber();
        		CIT.set_preselects(model);
        		CIT.set_form(model);
        		CIT.set_submit(model);
        		CIT.add_eventHandlers(model);
        		CIT.add_newRecordEventHandlers(model);
        		CIT.remove_loading_overlay();
        		break;
        	default:       	
        		document.getElementById('project_name').innerHTML = CIT._project.name;
        	CIT.set_preselects(model);
        	CIT.set_form(model);
        	CIT.set_submit(model);
        	CIT.add_eventHandlers(model);
        	CIT.add_newRecordEventHandlers(model);
        	CIT.remove_loading_overlay();
        	}
        },
        
        populate_transcriber: function () {
            var date;
            MAG.AUTH.get_user_info({'success': function(response) {
        	if (response.hasOwnProperty('ITSEE_id')) {
        	    document.getElementById('transcriber').value = response.ITSEE_id;
        	} else {
        	    document.getElementById('transcriber').value = response._id;
        	}
        	if (document.getElementById('transcriber_display')) {
        	    document.getElementById('transcriber_display').value = document.getElementById('transcriber').value;
        	}
            }});
            date = new Date();
            document.getElementById('transcription_date').value = date.getTime();
            document.getElementById('transcription_date_display').value = date.getDate() + '/' + (date.getMonth() + 1) + '/' + date.getFullYear();
        },

        add_newRecordEventHandlers: function(model) {
            switch (model) {
            case 'cit_author':
                MAG.EVENT.addEventListener(document.getElementById('abbreviation'), 'keyup', function(event){
                    CIT.update_identifier(model);
                });
                break;
            case 'cit_work':
                MAG.EVENT.addEventListener(document.getElementById('author_id'), 'change', function(event){
                    CIT.update_identifier(model);
                });
                MAG.EVENT.addEventListener(document.getElementById('abbreviation'), 'keyup', function(event){
                    CIT.update_identifier(model);
                });
                break;
            case 'cit_edition':
                MAG.EVENT.addEventListener(document.getElementById('work_id'), 'change', function(event){
                    CIT.update_identifier(model);
                });
                break;
            case 'cit_comcitation':
                MAG.EVENT.addEventListener(document.getElementById('work_id'), 'change', function(event){
                    CIT.update_identifier(model);
                });
                MAG.EVENT.addEventListener(document.getElementById('book'), 'change', function(event){
                    CIT.update_identifier(model);
                });
                MAG.EVENT.addEventListener(document.getElementById('chapter'), 'change', function(event){
                    CIT.update_identifier(model);
                });
                MAG.EVENT.addEventListener(document.getElementById('verse'), 'change', function(event){
                    CIT.update_identifier(model);
                });
                break;
            case 'cit_citation':
              MAG.EVENT.addEventListener(document.getElementById('work_id'), 'change', function(event){
        	  
                  CIT.update_identifier(model);
              });
              MAG.EVENT.addEventListener(document.getElementById('book'), 'change', function(event){
                  CIT.update_identifier(model);
              });
              MAG.EVENT.addEventListener(document.getElementById('chapter'), 'change', function(event){
                  CIT.update_identifier(model);
              });
              MAG.EVENT.addEventListener(document.getElementById('verse'), 'change', function(event){
                  CIT.update_identifier(model);
              });
              MAG.EVENT.addEventListener(document.getElementById('work_id'), 'change', function (event) {
        	  CIT.CIT.display_clavis(event.target.value);
              });
            }
        },

        add_eventHandlers: function(model) {
            var id_list, i;
            switch (model) {
            case 'cit_author':
                CIT.add_submitHandlers(model);
                CIT.add_validationHandlers(model);
                break;
            case 'cit_work':
                CIT.add_submitHandlers(model);
                CIT.add_validationHandlers(model);
                MAG.EVENT.addEventListener(document.getElementById('author_id'), 'change', function(event){
                    //see if its obsolete and if so check obsolete box for work
                    MAG.REST.apply_to_resource('cit_author', event.target.value, {'success': function(result) {
                        if (result.hasOwnProperty('obsolete')) {
                            document.getElementById('obsolete').checked = true;
                        } else {
                            document.getElementById('obsolete').checked = false;
                        }
                    }});
                });
                break;
            case 'cit_edition':
                CIT.add_submitHandlers(model);
                CIT.add_validationHandlers(model);
                MAG.EVENT.addEventListener(document.getElementById('author_id'), 'change', function(event){
                    CIT.filter_data(event.target.id, event.target.value, true);
                });
                MAG.EVENT.addEventListener(document.getElementById('delete_legacy_edition'), 'click', function() {
                    var conf;
                    conf = confirm('Are you sure you want to delete the legacy edition data?');
                    if (conf === true) {
                	document.getElementById('legacy_edition_hidden').value = '';
                	document.getElementById('legacy_edition_div').style.display = 'none';
                    } else {
                	return;
                    }
                });
                break;
            case 'cit_comcitation':
                CIT.add_submitHandlers(model);
                CIT.add_validationHandlers(model);
                id_list = ['book', 'chapter', 'verse', 'language'];
                for (i = 0; i < id_list.length; i += 1) {
                    MAG.EVENT.addEventListener(document.getElementById(id_list[i]), 'change', function() {
                        CIT.COMCIT.get_basetext(model);
                    });
                }
                MAG.EVENT.addEventListener(document.getElementById('author_id'), 'change', function(event){
                    CIT.filter_data(event.target.id, event.target.value, false);
                });
                MAG.EVENT.addEventListener(document.getElementById('work_id'), 'change', function(event){
                    CIT.filter_data(event.target.id, event.target.value, false);
                });
                MAG.EVENT.addEventListener(document.getElementById('is_ms'), 'click', function(event){
                    CIT.toggle_ms_edition(event.target.id);
                });
                MAG.EVENT.addEventListener(document.getElementById('reconstruction_checkbox'), 'click', function(event){
                    CIT.enable_formfield(event.target.id, 'exegesis_text');
                });
                MAG.EVENT.addEventListener(document.getElementById('add_lemma_extent'), 'click', function(event){
                    CIT.COMCIT.add_lemma_extent();
                });
                MAG.EVENT.addEventListener(document.getElementById('add_lemma_msvariant'), 'click', function(event){
                    CIT.COMCIT.add_lemma_msvariant();
                });
                MAG.EVENT.addEventListener(document.getElementById('delete_lemma_msvariant_0'), 'click', function(event){
                    CIT.COMCIT.delete_element(event.target.parentNode.parentNode.parentNode);
                });
                MAG.EVENT.addEventListener(document.getElementById('add_lemma_exegesis_diffs'), 'click', function(event){
                    CIT.COMCIT.add_lemma_exegesis_diffs();
                });
                MAG.EVENT.addEventListener(document.getElementById('delete_lemma_headword_0'), 'click', function(event){
                    CIT.COMCIT.delete_element(event.target.parentNode.parentNode.parentNode);
                });
                MAG.EVENT.addEventListener(document.getElementById('add_other_references'), 'click', function(event){
                    CIT.COMCIT.add_other_references();
                });
                MAG.EVENT.addEventListener(document.getElementById('delete_other_references_0'), 'click', function(event){
                    CIT.COMCIT.delete_element(event.target.parentNode.parentNode.parentNode);
                });

                MAG.EVENT.addEventListener(document.getElementById('lemma_text'), 'change', function(event){
                    CIT.COMCIT.update_lemma_reminder(event.target.value);
                    CIT.COMCIT.update_exegesis_text(event.target.value);
                });
                MAG.EVENT.addEventListener(document.getElementById('make_live'), 'click', function(event) {
                    document.getElementById('status').value = 'live';
                    document.getElementById('status_value').innerHTML = 'live';
                });
                MAG.EVENT.addEventListener(document.getElementById('flag'), 'click', function(event) {
                    if (document.getElementById('flag').value === 'Unflag') {
                        document.getElementById('status').value = document.getElementById('status').value.replace(' but flagged', '');
                        document.getElementById('status_value').innerHTML = document.getElementById('status_value').innerHTML.replace(' but flagged', '');                        
                        document.getElementById('flag').value = 'Flag for attention';
                    } else {
                        document.getElementById('status').value = document.getElementById('status').value + ' but flagged';
                        document.getElementById('status_value').innerHTML = document.getElementById('status_value').innerHTML +' but flagged';
                        document.getElementById('flag').value = 'Unflag';
                    }
                });
                if (document.getElementById('history_button') !== null) {
                    MAG.EVENT.addEventListener(document.getElementById('history_button'), 'click', function(event){
                        CIT.toggle_history(model);
                    });
                }
                break;
            case 'cit_citation' :
            	CIT.add_submitHandlers(model);
            	CIT.add_validationHandlers(model);
            	id_list = ['book', 'chapter', 'verse', 'language'];
            	for (i = 0; i < id_list.length; i += 1) {
            		MAG.EVENT.addEventListener(document.getElementById(id_list[i]), 'change', function() {
            			CIT.COMCIT.get_basetext(model);
            		});
            	}
            	MAG.EVENT.addEventListener(document.getElementById('author_id'), 'change', function(event) {
            		CIT.filter_data(event.target.id, event.target.value, false, CIT.CIT.display_extras);
            	});
            	MAG.EVENT.addEventListener(document.getElementById('work_id'), 'change', function(event) {
            		CIT.filter_data(event.target.id, event.target.value, false, CIT.CIT.display_extras);
            	});
            	MAG.EVENT.addEventListener(document.getElementById('edition_id'), 'change', function(event) {
            		CIT.CIT.show_edition_details(document.getElementById('edition_id').value);
            	});
            	MAG.EVENT.addEventListener(document.getElementById('add_manuscript_variants'), 'click', function(event) {
            		CIT.CIT.add_manuscript_variants();
            	});
            	MAG.EVENT.addEventListener(document.getElementById('add_dependencies'), 'click', function(event) {
            		CIT.CIT.add_dependencies();
            	});
            	MAG.EVENT.addEventListener(document.getElementById('add_parallel'), 'click', function(event) {
            		CIT.CIT.add_parallel();
            	}); 
            	MAG.EVENT.addEventListener(document.getElementById('add_catena'), 'click', function(event) {
            		CIT.CIT.add_catena();
            	});
            	//TODO: need to make sure buttons are set correctly for current status
            	MAG.EVENT.addEventListener(document.getElementById('flag'), 'click', function(event) {
            		if (document.getElementById('flag').value === 'Unflag') {
            			document.getElementById('status').value = document.getElementById('status').value.replace(' but flagged', '');
            			document.getElementById('status_value').innerHTML = document.getElementById('status_value').innerHTML.replace(' but flagged', '');                        
            			document.getElementById('flag').value = 'Flag for attention';
            		} else {
            			document.getElementById('status').value = document.getElementById('status').value + ' but flagged';
            			document.getElementById('status_value').innerHTML = document.getElementById('status_value').innerHTML +' but flagged';
            			document.getElementById('flag').value = 'Unflag';
            		}
            	});
            	MAG.EVENT.addEventListener(document.getElementById('deprecate'), 'click', function(event) {
            		if (document.getElementById('deprecate').value === 'Deprecate') {
            			document.getElementById('status').value = 'deprecated';
            			document.getElementById('status_value').innerHTML = 'Deprecated';
            			document.getElementById('deprecate').value = 'Make Live';
            			document.getElementById('flag').value = 'Flag for attention';
            		} else {
            			document.getElementById('status').value = 'Live';
            			document.getElementById('status_value').innerHTML = 'Live';
            			document.getElementById('deprecate').value = 'Deprecate';
            			document.getElementById('flag').value = 'Flag for attention';
            		}
            	});
            	break;
            default :
                CIT.add_submitHandlers(model);
                CIT.add_validationHandlers(model);
            }
        },

        //TODO: tidy this up so back parameter can be passed through if it is present
        add_submitHandlers: function(model) {
            var elem, param_dict, url, model_label;
            model_label = model.replace(CIT.model_namespace, '')
            elem = document.getElementById('submit_continue');
            if (elem) {
                MAG.EVENT.addEventListener(elem, 'click', function(event){
                    CIT.submit(model + '_form');
                });
            }
            elem = document.getElementById('submit_another');
            if (elem) {
                MAG.EVENT.addEventListener(elem, 'click', function(event){
                    CIT.submit(model + '_form', '/citations/' + model_label + '/edit/');
                });
            }
            elem = document.getElementById('submit_home');
            if (elem) {
                param_dict = MAG.URL.get_current_query();
                if (param_dict.hasOwnProperty('back')) {
                    url = param_dict.back;
                } else {
                    url = '/citations/' + model_label + '/';
                }
                MAG.EVENT.addEventListener(elem, 'click', function(event){
                    CIT.submit(model + '_form', url);
                });
            }
            elem = document.getElementById('submit_same');
            if (elem) {
                MAG.EVENT.addEventListener(elem, 'click', function(event){
                    CIT.submit(model + '_form', 'same');
                });
            }
            elem = document.getElementById('submit_next');
            if (elem) {
                MAG.EVENT.addEventListener(elem, 'click', function(event){
                    CIT.submit(model + '_form', 'next');
                });
            }
            elem = document.getElementById('submit_next_record');
            if (elem) {
                MAG.EVENT.addEventListener(elem, 'click', function(event){
                    CIT.submit(model + '_form', 'record');
                });
            }
            elem = document.getElementById('reset_form');
            if (elem) {
                MAG.EVENT.addEventListener(elem, 'click', function(event){
                    window.location.reload(false);
                });
            }
            elem = document.getElementById('delete');
            if (elem) {
                MAG.EVENT.addEventListener(elem, 'click', function(event){
                    CIT.confirm_delete(model);
                });
            }
        },

        add_validationHandlers: function(model) {
            var elems, alt_elems, i, start, end;
            elems = document.getElementById(model + '_form').elements;
            for (i = 0; i < elems.length; i += 1) {
                if (elems[i].tagName === 'TEXTAREA' || elems[i].tagName === 'SELECT'
                    || (elems[i].tagName === 'INPUT' && elems[i].type === 'text')) {
                    MAG.EVENT.add_event(elems[i], 'change', function(event){
                        CIT.validate_element(event.target);
                    }, 'basic_validation');
                }
            }
            if (model === 'cit_comcitation') {
                alt_elems = [document.getElementById('is_ms'), document.getElementById('edition_id'), document.getElementById('ms_siglum')];
                for (i = 0; i < alt_elems.length; i += 1) {
                    MAG.EVENT.addEventListener(alt_elems[i], 'change', function(event) {
                       if (document.getElementById('is_ms').checked === true) {
                           if (document.getElementById('ms_siglum').value === '') {
                               MAG.ELEMENT.add_className(document.getElementById('ms_siglum').parentNode, 'missing');
                           } else {
                               MAG.ELEMENT.remove_className(document.getElementById('ms_siglum').parentNode, 'missing');
                           }
                           MAG.ELEMENT.remove_className(document.getElementById('edition_id').parentNode, 'missing');
                       } else {
                           if (document.getElementById('edition_id').value === 'none') {
                               MAG.ELEMENT.add_className(document.getElementById('edition_id').parentNode, 'missing');
                           } else {
                               MAG.ELEMENT.remove_className(document.getElementById('edition_id').parentNode, 'missing');
                           }
                           MAG.ELEMENT.remove_className(document.getElementById('ms_siglum').parentNode, 'missing');
                       }
                    });
                }
                i = 0;
                while (document.getElementById('lemma_extent_' + i + '_start')) {
                    start = document.getElementById('lemma_extent_' + i + '_start');
                    end = document.getElementById('lemma_extent_' + i + '_end');
                    MAG.EVENT.remove_event('basic_validation', {'element': start});
                    MAG.EVENT.add_event(start, 'change', function(event) {
                        CIT.validate_elem_regex(event.target, /^\d{1,2}:\d{1,2}[a-z]?$/);
                    }, 'regex_validation');
                    MAG.EVENT.remove_event('basic_validation', {'element': end});
                    MAG.EVENT.add_event(end, 'change', function(event) {
                        CIT.validate_elem_regex(event.target, /^\d{1,2}:\d{1,2}[a-z]?$/);
                    }, 'regex_validation');
                    i += 1;
                }
            }
        },
        
        set_project_cookie: function (project_id, status) {
	    document.cookie = 'project=' + project_id;
	    if (typeof status !== 'undefined') {
		document.cookie = 'status=' + status;
	    }
	},
	
	delete_citation_cookies: function () {
	    document.cookie="project=; path=/citations/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
	    document.cookie="status=; path=/citations/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
	},
	
	get_project_cookie: function (target) {
	    var cookie_pairs, pair, i, name;
	    cookie_pairs = document.cookie.split(';');
	    name = target + '=';
	    for (i = 0; i < cookie_pairs.length; i += 1) {
		pair = cookie_pairs[i].trim();
		if (pair.indexOf(name) === 0) {
		    return pair.substring(name.length, pair.length);
		}
	    }
	    return '';
	},
	
        show_loading_overlay: function (message) {
            var overlay, opts, target, message_el;
            if (!document.getElementById('overlay')) {
        	overlay = document.createElement('div');
                overlay.id = 'overlay';
                message_el = document.createElement('div');
                message_el.id = 'overlay_message';
                if (typeof message !== 'undefined') {
            	message_el.innerHTML = '<p class="center">' + message + '</p>';
                }
                document.getElementsByTagName('body')[0].appendChild(overlay);
                document.getElementsByTagName('body')[0].appendChild(message_el);
                opts = {
            	    lines: 13, // The number of lines to draw
            	    length: 20, // The length of each line
            	    width: 10, // The line thickness
            	    radius: 30, // The radius of the inner circle
            	    corners: 1, // Corner roundness (0..1)
            	    rotate: 0, // The rotation offset
            	    direction: 1, // 1: clockwise, -1: counterclockwise
            	    color: '#000', // #rgb or #rrggbb or array of colors
            	    speed: 1, // Rounds per second
            	    trail: 60, // Afterglow percentage
            	    shadow: false, // Whether to render a shadow
            	    hwaccel: false, // Whether to use hardware acceleration
            	    className: 'spinner', // The CSS class to assign to the spinner
            	    zIndex: 2e9, // The z-index (defaults to 2000000000)
            	    top: '50%', // Top position relative to parent
            	    left: '50%' // Left position relative to parent
                };
                target = document.getElementsByTagName('body')[0];
                CIT.spinner = new Spinner(opts).spin(target);
            }
            return;
        },
        
        remove_loading_overlay: function () {
            CIT.spinner.stop();
            if (document.getElementById('overlay')) {
        	document.getElementsByTagName('body')[0].removeChild(document.getElementById('overlay'));
            }
            if (document.getElementById('overlay_message')) {
        	document.getElementsByTagName('body')[0].removeChild(document.getElementById('overlay_message'));
            }
            return;
        },


        // End of module
    };
}());

