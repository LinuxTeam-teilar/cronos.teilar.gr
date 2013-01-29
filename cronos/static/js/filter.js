/* Init */
eval( $("script#filter").text() );
Filter['BEGIN']();
AllEntries = $(Entry['Entry']);

/* Update list to match filter's text */
UpdateEntryVisibility = function(){

	/* Match Text */
	EntriesMatched = AllEntries.filter(
			/* Need to be done throught a function
			 * because jquery doesn't evaluate descent operators linke > in .find() selectors */
			function(){
				return $(this).find( Entry['TextString']+':contains("' +SearchBox['Text'].val()+ '")' ).length == 1 ;
			}
			);

	/* Submatch group */
	if( SearchBox['Group'].attr('checked') ){
		EntriesMatched = EntriesMatched.filter(
				/* Same reason as above */
				function(){
					return $(this).find( Entry['Group'] ).length == 1;
				}
			);
	}

	EntriesMatched.not( ':visible' ).show();
	AllEntries.not( EntriesMatched ).hide();
	SearchBox['MatchedLength'].text( AllEntries.filter(':visible').length )
};

/* Initialize Filter */
SearchBox['SearchBox'].show();
SearchBox['Text'].attr( 'value', '' );
SearchBox['Text'].bind( 'keyup', UpdateEntryVisibility );
SearchBox['Group'].bind( 'keypress click', UpdateEntryVisibility );
SearchBox['MatchedLength'].text( AllEntries.length );

/* Final touches */
Filter['END']();
Filter = undefined;
