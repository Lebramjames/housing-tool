"""
2025-06-19 16:48:25,025 - INFO - Successfully retrieved page: https://www.demakelaers.nl/aanbod/woningaanbod/AMSTERDAM/50+woonopp/-500000/koop/1+kamers/
De Makelaers B.V.
,
			disableHI: true
						, pathClass: 'sfSelected'		});

	});

	
</script>

</div><div class="navRight" id="generated_id22921_16641226"></div></div></div></div><div id="kadercontent"><div id="bodycontent"><div class="breadcrumbswrapper" id="generated_id22921_16643965"><div id="generated_id22921_16643966" class="breadcrumbs" itemscope itemtype="http://schema.org/BreadcrumbList">
				
		
					<div class="crumb " itemprop="itemListElement" itemscope itemtype="http://schema.org/ListItem"><a href="/" itemscope itemtype="http://schema.org/Thing" itemprop="item" itemid="/"><span itemprop="name">Home&nbsp;</span></a><meta itemprop="position" content="1" /> &gt;</div>
					
		
					<div class="crumb" itemprop="itemListElement" itemscope itemtype="http://schema.org/ListItem"><span itemprop="name">Wonen</span><meta itemprop="position" content="2" /></div>
			</div>
</div><script>
setCookie('wonenAanbodGroup', window.location.pathname + window.location.search);
</script>
<script type="text/javascript">
jQuery(document).ready(function(){
	if (jQuery('#generated_id22921_16644235').is(':visible')) {
		setTimeout(applyMasonrygenerated_id22921_16644235, 0);
	}
});

function applyMasonrygenerated_id22921_16644235() {
	var oElem = jQuery('#generated_id22921_16644235');
	var iWidth = oElem.width() / 12;
	oElem.masonry({
					percentPosition: true,
			columnWidth: '.blok-sizer',
						itemSelector: '.blok',
		isInitLayout: false
});

	/*
	 * Omdat sommige versies van Masonry veroudert zijn op custom websites. En
	 * dus geen event kunnen binden met 'on'. Checken we of oElem.on wel een functie is.
	 */ 
	if (typeof oElem.on == 'function') { 
		oElem.on('layoutComplete', addBlokRowClass);
	}

	
	oElem.masonry();
}




function addBlokRowClass(event, items ) {
	var posY = 0;
	var className = "blokRowEven";
	var firstRow = true;

	for (i=0;i<items.length;i++){
		var jBlok = jQuery(items[i].element);
		/* Append de blokRowEven of blokRowOdd klasse als de Y position (row positie)
		 * overeenkomt. En verwijder de eventuele bestaande blokRowEven blokRowOdd
		 * klass zodat je geen dubbele klasses.
		 */
		if (items[i].position.y == posY) {
			jBlok.removeClass( "blokRowEven blokRowOdd firstRow" ).addClass( className );
			if (firstRow) {
				jBlok.addClass('firstRow');
			}
		} else {
			if (firstRow) {
				firstRow = false;
			}
			posY = items[i].position.y;
			(className == "blokRowEven") ? className = "blokRowOdd" : className = "blokRowEven"; 
			jBlok.removeClass( "firstRow blokRowEven blokRowOdd" ).addClass( className );
		}
	}

	
}
</script>
<div id="generated_id22921_16644235" class="blokLayout al2 ">
			<div class="blok-sizer"></div>
		<div id="generated_id22921_16644340" class="blok zoekformAanbodlijstBlok roundedCorners rc10 white blok1van3breed blok1hoog">
	<div class="top">
		<div class="center column"></div>
		<div class="left column"></div>
		<div class="right column"></div>
	</div>
	<div class="middle">
		<div class="center column">
					<div class="aanbodZoekenTitel" id="generated_id22921_16644342">	<H1 id="generated_id22921_16644346"><span id="generated_id22921_16644347">Zoeken in</span>
<span id="pagina-informatie" class="section pagina-informatie" >
	<span>
		<span class="objecten-gevonden"> <span class="totaal-aantal-objecten" style="font-weight: bold;">35</span> woningen </span>
					<span class="seperator"> | </span>
			<span class="eerste-laatste"><span class="objecten-getoond-vanaf" style="font-weight: bold;">1</span> - <span class="objecten-getoond-tot" style="font-weight: bold;">0</span> getoond</span>
			</span>
</span>
</H1>

</div><script>
jQuery(function(){
	jQuery("#generated_id22921_16644349").tabs({
									active: (1-1)
																});
																											
	
			jQuery('#generated_id22921_16644349 > ul > li.tabMenuItem a').click(remasongenerated_id22921_16644349);
	});

function remasongenerated_id22921_16644349() {
		applyMasonrygenerated_id22921_16644235();
}

</script>

<div id="generated_id22921_16644349" class="">
	<ul class="tabsMenu ogZoekFormTabs">
									<li id="generated_id22921_16644350" class="tabMenuItem ">
					<span>
						<a href="#Beide" id="tabItem_Beide">
							<span>
								Beide
							</span>
						</a>
					</span>
				</li>
												<li id="generated_id22921_16644378" class="tabMenuItem ">
					<span>
						<a href="#Koop" id="tabItem_Koop">
							<span>
								Koop
							</span>
						</a>
					</span>
				</li>
												<li id="generated_id22921_16644409" class="tabMenuItem ">
					<span>
						<a href="#Huur" id="tabItem_Huur">
							<span>
								Huur
							</span>
						</a>
					</span>
				</li>
						</ul>
	<div class="tabContainer">
									<div id="Beide" class=""><form id="wonenzoekformulier" class="ogZoekform aanbodZoeken" action="/aanbod/woningaanbod/">
	<div class="row allesfields" id="generated_id22921_16644352">	<input id="generated_id22921_16644353" type="hidden" name="inclkoop" value="true" />

	<input id="generated_id22921_16644354" type="hidden" name="inclhuur" value="true" />

	<div id='field_wonen_beide_cities' class='editfieldoutertag  editfieldcombofieldfilter outertagplaats plaats'><span id='field_wonen_beide_cities_label_span' class='entlabel'>
<label class='entlabel small' for='cities'>Plaats</label>
</span>
<span id='field_wonen_beide_cities_input_td' class='entview'>
		<select name="cities">
					<option value="">Plaats</option>
							<option value="ALKMAAR" data-province="Noord-Holland" >
				Alkmaar			</option>
					<option value="ALMERE" data-province="Flevoland" >
				Almere			</option>
					<option value="AMSTELVEEN" data-province="Noord-Holland" >
				Amstelveen			</option>
					<option value="AMSTERDAM" selected data-province="Noord-Holland" >
				Amsterdam			</option>
					<option value="ASSENDELFT" data-province="Noord-Holland" >
				Assendelft			</option>
					<option value="BADHOEVEDORP" data-province="Noord-Holland" >
				Badhoevedorp			</option>
					<option value="BERGEN (NH)" data-province="Noord-Holland" >
				Bergen (NH)			</option>
					<option value="BEVERWIJK" data-province="Noord-Holland" >
				Beverwijk			</option>
					<option value="HOOFDDORP" data-province="Noord-Holland" >
				Hoofddorp			</option>
					<option value="JISP" data-province="Noord-Holland" >
				Jisp			</option>
					<option value="KOOG AAN DE ZAAN" data-province="Noord-Holland" >
				Koog aan de Zaan			</option>
					<option value="KROMMENIE" data-province="Noord-Holland" >
				Krommenie			</option>
					<option value="KUDELSTAART" data-province="Noord-Holland" >
				Kudelstaart			</option>
					<option value="PURMEREND" data-province="Noord-Holland" >
				Purmerend			</option>
					<option value="UITGEEST" data-province="Noord-Holland" >
				Uitgeest			</option>
					<option value="UITHOORN" data-province="Noord-Holland" >
				Uithoorn			</option>
					<option value="WESTZAAN" data-province="Noord-Holland" >
				Westzaan			</option>
					<option value="WORMER" data-province="Noord-Holland" >
				Wormer			</option>
					<option value="WORMERVEER" data-province="Noord-Holland" >
				Wormerveer			</option>
					<option value="ZAANDAM" data-province="Noord-Holland" >
				Zaandam			</option>
					<option value="ZAANDIJK" data-province="Noord-Holland" >
				Zaandijk			</option>
			</select>
	</span></div>
	
<div id='field_straal' class='editfieldoutertag  editfieldafstandsearch outertagstraal straal'><span id='field_straal_label_span' class='entlabel'>
<label class='entlabel header' for='straal'>Straal</label>
</span>
<span id='field_straal_input_td' class='entview'>
<select name="straal">
			<option value="-1" >Straal</option>
			<option value="1" >1 km</option>
			<option value="2" >2 km</option>
			<option value="5" >5 km</option>
			<option value="10" >10 km</option>
			<option value="15" >15 km</option>
	</select>
</span></div>

	<div id='field_generated_id22921_16644356' class='editfieldoutertag  editfieldfilteredautocomplete outertagstraat straat'><span id='field_generated_id22921_16644356_label_span' class='entlabel'>
<label class='entlabel small' for='street'>Straat</label>
</span>
<span id='field_generated_id22921_16644356_input_td' class='entview'>
	<span class="ac_span">
		<input class="ac_input" type="text" name="street" placeholder='Straat' />
	</span>
	</span></div>
	<script type="text/javascript">
jQuery(document).ready(function(){
	var options = [
							'Abbringstraat',					'Admiralengracht',					'Akkerland',					'Alkmaarstraat',					'Amundsenweg',					'Anderiesenstraat',					'Andries Copierstraat',					'Arisstraat',					'Barcelonaplein',					'Berceusestraat',					'Bergerweg',					'Beukenweg',					'Bijlstraat',					'Bilderdijkstraat',					'Blokmaalder',					'Bloys van Treslongstraat',					'Boekenbergpark',					'Bonaireplein',					'Boomgaardlaan',					'Bos en Lommerweg',					'Boterbloemstraat',					'Braillestraat',					'Buitenpoort',					'Burgemeester Hogguerstraat',					'Burgemeester Ter Laanstraat',					'Burgemeester van der Wartstraat',					'Cannenburg',					'Chet Bakerstraat',					'Da Costastraat',					'Davisstraat',					'De Achterhoede',					'De Clercqstraat',					'De Schoolmeesterstraat',					'De Weer',					'Derde Oosterparkstraat',					'Derkinderenstraat',					'Dokkumerdiep',					'Dorpsstraat',					'Dr. J.J. van der Horststraat',					'Ds. Martin Luther Kingweg',					'Dubbelebuurt',					'Eastonstraat',					'Eerste Atjehstraat',					'Eerste Helmersstraat',					'Eerste Keucheniusstraat',					'Eerste Van Swindenstraat',					'Elandsgracht',					'Fleerde',					'Ganimedesstraat',					'Gele Ring',					'Geuzenkade',					'Geuzenstraat',					'Gouden Leeuw',					'Haarlemmerweg',					'Harry Koningsbergerstraat',					'Haya van Someren-Downerstraat',					'Heiligeweg',					'Heintje Hoekssteeg',					'Herculesstraat',					'Het Hoogt',					'Het Prinsenhofstraat',					'Hofakker',					'Hollandsch Diep',					'Hoofdweg',					'IJdoornlaan',					'IJplein',					'IJselstraat',					'Irawan Soejonostraat',					'J.M. den Uylstraat',					'Jacob de Rijkhof',					'Jacob van Lennepstraat',					'James Rosskade',					'Jan Bestevaerstraat',					'Jan de Louterstraat',					'Jan den Haenstraat',					'Jan Evertsenstraat',					'Jasonstraat',					'Jennerstraat',					'Johannes Verhulststraat',					'Joris Ivensplein',					'Jubelpark',					'Jupiterstraat',					'Juttepeerpad',					'Kamerlingh Onneslaan',					'Kanaalstraat',					'Kattenburgerhof',					'Kaukasus',					'Kollergang',					'Koopvaardijstraat',					'Kortrijk',					'Krommeniedijk',					'Kruiskamplaan',					'Laagte Kadijk',					'Laan van Vlaanderen',					'Lagedijk',					'Langswater',					'Lauriergracht',					'Leen Jongewaardkade',					'Letterhout',					'Lia Doranastraat',					'Loenermark',					'Lomanstraat',					'Loodgieter',					'Lumierestraat',					'Luxemburglaan',					'Maimonideslaan',					'Maria Austriastraat',					'Mauritskade',					'Meander',					'Medanplantsoen',					'Meeuwstraat',					'Meidoornlaan',					'Middel',					'Militaireweg',					'Molenstraat',					'NDSM-straat',					'Nellen Weer',					'Nieuwe Leliestraat',					'Nieuwpoortstraat',					'Noorderhoofdstraat',					'Oldenaller',					'Opera',					'Orion',					'Osdorper Ban',					'Osdorperweg',					'Pieter Jelles Troelstralaan',					'Pieter van der Doesstraat',					'Piraeushaven',					'Populierenlaan',					'Prins Bernhardplein',					'Prins Hendrikstraat',					'Provincialeweg',					'Pruikenmakerstraat',					'Reigerstraat',					'Reinwardtstraat',					'Reitdiep',					'Rietwijkerstraat',					'Rietwijkstraat',					'Robert Fruinlaan',					'Rode Ring',					'Rombout Hogerbeetsstraat',					'Saturnusstraat',					'Schaarbeekstraat',					'Schaarsven',					'Schaatsenrijder',					'Schrijvertje',					'Schweitzerstraat',					'Sierra Nevada',					'Silenestraat',					'Sluisstraat',					'Soldaatje',					'Spaarndammerstraat',					'Stadskwekerij',					'Steinerbos',					'Teldershof',					'Thamerweg',					'Titanialaan',					'Tolstoistraat',					'Triangelhof',					'Trimurtistraat',					'Tweede Keucheniusstraat',					'Uiterwaardenstraat',					'Valentijnkade',					'Valkstraat',					'Van Gentstraat',					'Van Hallstraat',					'Van Hogendorpstraat',					'Van Nijenrodeweg',					'Van Spilbergenstraat',					'Van Woustraat',					'Vlietsend',					'Vogezen',					'Voornsehoek',					'Weeshuissteeg',					'Wijnmalenstraat',					'Wilhelminastraat',					'Willem de Zwijgerlaan',					'Wolbrantskerkweg',					'Zeemansstraat',					'Zilverschoonlaan',					'Zilverschoonplein',					'Zomerzon',					'Zuiddijk',					'Zuiderhoofdstraat',			];
	$('#field_generated_id22921_16644356 input').autocomplete(options, {
		mustMatch: true,
		matchContains: false,
		max: 20,
		noRecord: "Geen resultaat"
	});
	});
	</script>

</div>	<input id="generated_id22921_16644369" type="hidden" name="bouwvorm" value="" />

	<input id="generated_id22921_16644370" type="hidden" name="resultsPerPage" value="" />

	<input id="generated_id22921_16644371" type="hidden" name="objecttype" value="" />

	<div class="row additionalsearchcriteria" id="generated_id22921_16644372"><div id='field_numberofroomsfrom' class='editfieldoutertag  editfieldaantalsearch outertagleft left'><span id='field_numberofroomsfrom_label_span' class='entlabel'>
<label class='entlabel header' for='numberofroomsfrom'>Aantal kamers:</label>
</span>
<span id='field_numberofroomsfrom_input_td' class='entview'>
<select name="numberofroomsfrom">
			<option value="-1" >Aantal kamers</option>
			<option value="1"  selected>1+</option>
			<option value="2" >2+</option>
			<option value="3" >3+</option>
			<option value="4" >4+</option>
			<option value="5" >5+</option>
	</select>
</span></div>

<div id='field_woonoppfrom' class='editfieldoutertag  editfieldoppervlaktesearch outertagright right'><span id='field_woonoppfrom_label_span' class='entlabel'>
<label class='entlabel header' for='woonoppfrom'>Woonoppervlakte:</label>
</span>
<span id='field_woonoppfrom_input_td' class='entview'>
<select name="woonoppfrom">
			<option value="-1" >Woon.opp.</option>
			<option value="50"  selected>50+ m&sup2;</option>
			<option value="75" >75+ m&sup2;</option>
			<option value="100" >100+ m&sup2;</option>
			<option value="150" >150+ m&sup2;</option>
			<option value="250" >250+ m&sup2;</option>
	</select>
</span></div>

</div>	<input id="generated_id22921_16644375" type="hidden" name="transactiestatus" value="" />


	<div id="wonenzoekformulier-submit" class="form-submit">
		<input type="submit" name="formulier-submit-wonenzoekformulier" value="Zoeken" />
	</div>
</form>

	<script type="text/javascript">
jQuery(document).ready(function() {
	var oForm = jQuery("#wonenzoekformulier");
	if (!oForm.find('input[name="module"]')[0]) {
		var sModule = 'wonen';
		if (sModule == 'null') {
			alert("Kan niet beslissen welke module hoort bij dit zoekformulier!");
			return;
		}
		jQuery('<input type="hidden" name="module" value="' + sModule + '" />').appendTo(oForm);
		
			}
	oForm.submit(function() {
		var params = {};
		oForm.find("input:not(:submit),select").not("[disabled]").each(function (index, elem){
			var name = $(elem).attr("name");
			params[name] = ''; // simuleer een set, de waarde is niet relevant
		});
		for (name in params) {
			var value = oForm.find("[name=" + name +"]") .fieldValue();
			if (!value[0]) {
				continue;
			}
			params[name] = value.join(",");
		}
		
				jQuery.getJSON(
				'/UrlZoekCriteriaBuilder/',
				params,
				function(data) {
											
						window.location.href = data.url;
									});
			return false;
			});
});
	</script>

</div>
												<div id="Koop" class=""><form id="generated_id22921_16644380" class="ogZoekform aanbodZoeken koopWoningenZoekformulier" action="/aanbod/woningaanbod/">
	<div class="row koopfields" id="generated_id22921_16644381">	<input id="generated_id22921_16644382" type="hidden" name="inclkoop" value="true" />

	<input id="generated_id22921_16644383" type="hidden" name="inclhuur" value="false" />

	<div id='field_wonen_koop_cities' class='editfieldoutertag  editfieldcombofieldfilter outertagplaats plaats'><span id='field_wonen_koop_cities_label_span' class='entlabel'>
<label class='entlabel small' for='cities'>Plaats</label>
</span>
<span id='field_wonen_koop_cities_input_td' class='entview'>
		<select name="cities">
					<option value="">Plaats</option>
							<option value="ALKMAAR" data-province="Noord-Holland" >
				Alkmaar			</option>
					<option value="ALMERE" data-province="Flevoland" >
				Almere			</option>
					<option value="AMSTELVEEN" data-province="Noord-Holland" >
				Amstelveen			</option>
					<option value="AMSTERDAM" selected data-province="Noord-Holland" >
				Amsterdam			</option>
					<option value="ASSENDELFT" data-province="Noord-Holland" >
				Assendelft			</option>
					<option value="BADHOEVEDORP" data-province="Noord-Holland" >
				Badhoevedorp			</option>
					<option value="BERGEN (NH)" data-province="Noord-Holland" >
				Bergen (NH)			</option>
					<option value="BEVERWIJK" data-province="Noord-Holland" >
				Beverwijk			</option>
					<option value="HOOFDDORP" data-province="Noord-Holland" >
				Hoofddorp			</option>
					<option value="JISP" data-province="Noord-Holland" >
				Jisp			</option>
					<option value="KOOG AAN DE ZAAN" data-province="Noord-Holland" >
				Koog aan de Zaan			</option>
					<option value="KROMMENIE" data-province="Noord-Holland" >
				Krommenie			</option>
					<option value="KUDELSTAART" data-province="Noord-Holland" >
				Kudelstaart			</option>
					<option value="PURMEREND" data-province="Noord-Holland" >
				Purmerend			</option>
					<option value="UITGEEST" data-province="Noord-Holland" >
				Uitgeest			</option>
					<option value="UITHOORN" data-province="Noord-Holland" >
				Uithoorn			</option>
					<option value="WESTZAAN" data-province="Noord-Holland" >
				Westzaan			</option>
					<option value="WORMER" data-province="Noord-Holland" >
				Wormer			</option>
					<option value="WORMERVEER" data-province="Noord-Holland" >
				Wormerveer			</option>
					<option value="ZAANDAM" data-province="Noord-Holland" >
				Zaandam			</option>
					<option value="ZAANDIJK" data-province="Noord-Holland" >
				Zaandijk			</option>
			</select>
	</span></div>
	
<div id='field_straal' class='editfieldoutertag  editfieldafstandsearch outertagstraal straal'><span id='field_straal_label_span' class='entlabel'>
<label class='entlabel header' for='straal'>Straal</label>
</span>
<span id='field_straal_input_td' class='entview'>
<select name="straal">
			<option value="-1" >Straal</option>
			<option value="1" >1 km</option>
			<option value="2" >2 km</option>
			<option value="5" >5 km</option>
			<option value="10" >10 km</option>
			<option value="15" >15 km</option>
	</select>
</span></div>

	<div id='field_generated_id22921_16644385' class='editfieldoutertag  editfieldfilteredautocomplete outertagstraat straat'><span id='field_generated_id22921_16644385_label_span' class='entlabel'>
<label class='entlabel small' for='street'>Straat</label>
</span>
<span id='field_generated_id22921_16644385_input_td' class='entview'>
	<span class="ac_span">
		<input class="ac_input" type="text" name="street" placeholder='Straat' />
	</span>
	</span></div>
	<script type="text/javascript">
jQuery(document).ready(function(){
	var options = [
							'Abbringstraat',					'Admiralengracht',					'Akkerland',					'Alkmaarstraat',					'Amundsenweg',					'Anderiesenstraat',					'Andries Copierstraat',					'Arisstraat',					'Barcelonaplein',					'Berceusestraat',					'Bergerweg',					'Beukenweg',					'Bijlstraat',					'Bilderdijkstraat',					'Blokmaalder',					'Bloys van Treslongstraat',					'Boekenbergpark',					'Bonaireplein',					'Bo
Nieuw
Het Hoogt 176 in Amsterdam 1025 HD Het Hoogt 176 in Amsterdam 1025 HD
Vraagprijs € 375.000,- k.k.
Soort object Appartement
Bouwjaar 1968
Bouwvorm Bestaande bouw
Woonoppervlakte 68 m²
Inhoud 232 m³

"""

from bs4 import BeautifulSoup

def extract_demakelaers_data(html: str):
    return None