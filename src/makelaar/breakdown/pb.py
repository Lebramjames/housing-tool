"""
2025-06-19 17:05:15,131 - INFO - Successfully retrieved page: https://www.pbmakelaars.nl/aanbod/woningaanbod/AMSTERDAM/50+woonopp/-500000/koop/1+kamers/
PB Makelaars o.z.
em-right"></span>
			</a>
							<ul class="dropDown ons_team empty">
									</ul>
					</li>
								<li class="menuitem_overons_vestigingen ">
			<a class="sub " title="Ons kantoor" href="/overons/vestigingen/" >
				<span class="menu-item-left"></span><span class="menu-item-mid">Ons kantoor</span><span class="menu-item-right"></span>
			</a>
							<ul class="dropDown ons_kantoor empty">
									</ul>
					</li>
								<li class="menuitem_beoordelingen ">
			<a class="sub " title="Hoe anderen ons ervaren" href="/beoordelingen/" >
				<span class="menu-item-left"></span><span class="menu-item-mid">Hoe anderen ons ervaren</span><span class="menu-item-right"></span>
			</a>
							<ul class="dropDown hoe_anderen_ons_ervaren empty">
									</ul>
					</li>
													</ul>
					</li>
								<li class="menuitem_overons_contact ">
			<a class="top " title="Contact" href="/overons/contact/" >
				<span class="menu-item-left"></span><span class="menu-item-mid">Contact</span><span class="menu-item-right"></span>
			</a>
							<ul class="dropDown contact empty">
									</ul>
					</li>
					</ul>
	
	
	</nav>

<script> 
	$(document).ready(function(){ 
		$("ul#generated_id25681_18912978 li ul li").parent().parent().children('a.top')
		.addClass('sf-with-ul')
		.children('.menu-item-mid')
		.append('<span class="sf-sub-indicator"></span>'); 	//Voegt pijltes aan menu items die submenu hebben  

		$("ul#generated_id25681_18912978 li ul li.selected").parent().parent().addClass("parent-of-selected sfSelected"); //Voegt classe aan menu items die selected submenu item hebben
		
		
		
		var navU = navigator.userAgent.toString().toLowerCase();
		var isIE10 = navU.indexOf("trident/6")>-1;
		if (isIE10) {
			$("ul#generated_id25681_18912978 > li > a").click(function(){
				if(jQuery(this).attr("target") == "_blank"){
					window.open(jQuery(this).attr("href"));
				} else {
					window.location.href = jQuery(this).attr("href");
				}
				return false;
			});
		}
		
		// http://users.tpg.com.au/j_birch/plugins/superfish/
		$("ul#generated_id25681_18912978").superfish({ 
			hoverClass: 'menu-hover',
			delay: 1000,
			speed: 'fast',
			autoArrows: false, //Met 'true' krijgen alle menu items pijltjes, zelfs met lege submenu
			dropShadows: false,
			disableHI: true
						, pathClass: 'sfSelected'		});

	});

	
</script>

</div><div class="navRight" id="generated_id25681_18912979"></div></div></div></div><div id="kadercontent"><div id="bodycontent"><div class="breadcrumbswrapper" id="generated_id25681_18915718"><div id="generated_id25681_18915719" class="breadcrumbs" itemscope itemtype="http://schema.org/BreadcrumbList">
				
		
					<div class="crumb " itemprop="itemListElement" itemscope itemtype="http://schema.org/ListItem"><a href="/" itemscope itemtype="http://schema.org/Thing" itemprop="item" itemid="/"><span itemprop="name">Home&nbsp;</span></a><meta itemprop="position" content="1" /> &gt;</div>
					
		
					<div class="crumb" itemprop="itemListElement" itemscope itemtype="http://schema.org/ListItem"><span itemprop="name">Wonen</span><meta itemprop="position" content="2" /></div>
			</div>
</div><script>
setCookie('wonenAanbodGroup', window.location.pathname + window.location.search);
</script>
<script type="text/javascript">
jQuery(document).ready(function(){
	if (jQuery('#generated_id25681_18915988').is(':visible')) {
		setTimeout(applyMasonrygenerated_id25681_18915988, 0);
	}
});

function applyMasonrygenerated_id25681_18915988() {
	var oElem = jQuery('#generated_id25681_18915988');
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
<div id="generated_id25681_18915988" class="blokLayout al2 zonderGoogleMaps">
			<div class="blok-sizer"></div>
		<div id="generated_id25681_18915991" class="blok zoekformAanbodlijstBlok zonderGooglemaps roundedCorners rc10 white blok1van1breed blok1hoog">
	<div class="top">
		<div class="center column"></div>
		<div class="left column"></div>
		<div class="right column"></div>
	</div>
	<div class="middle">
		<div class="center column">
					<div class="aanbodZoekenTitel" id="generated_id25681_18915993">	<h1 id="generated_id25681_18915995">Zoeken in ons aanbod</h1></div><script>
jQuery(function(){
	jQuery("#generated_id25681_18916000").tabs({
									active: (1-1)
																});
																											
	
			jQuery('#generated_id25681_18916000 > ul > li.tabMenuItem a').click(remasongenerated_id25681_18916000);
	});

function remasongenerated_id25681_18916000() {
		applyMasonrygenerated_id25681_18915988();
}

</script>

<div id="generated_id25681_18916000" class="">
	<ul class="tabsMenu ogZoekFormTabs">
									<li id="generated_id25681_18916001" class="tabMenuItem ">
					<span>
						<a href="#Beide" id="tabItem_Beide">
							<span>
								Beide
							</span>
						</a>
					</span>
				</li>
												<li id="generated_id25681_18916029" class="tabMenuItem ">
					<span>
						<a href="#Koop" id="tabItem_Koop">
							<span>
								Koop
							</span>
						</a>
					</span>
				</li>
												<li id="generated_id25681_18916060" class="tabMenuItem ">
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
	<div class="row allesfields" id="generated_id25681_18916003">	<input id="generated_id25681_18916004" type="hidden" name="inclkoop" value="true" />

	<input id="generated_id25681_18916005" type="hidden" name="inclhuur" value="true" />

	<div id='field_wonen_beide_cities' class='editfieldoutertag  editfieldcombofieldfilter outertagplaats plaats'><span id='field_wonen_beide_cities_label_span' class='entlabel'>
<label class='entlabel small' for='cities'>Plaats</label>
</span>
<span id='field_wonen_beide_cities_input_td' class='entview'>
		<select name="cities">
					<option value="">Plaats</option>
							<option value="AMSTERDAM" selected data-province="Noord-Holland" >
				Amsterdam			</option>
					<option value="DEVENTER" data-province="Overijssel" >
				Deventer			</option>
					<option value="DIEMEN" data-province="Noord-Holland" >
				Diemen			</option>
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

	<div id='field_generated_id25681_18916007' class='editfieldoutertag  editfieldfilteredautocomplete outertagstraat straat'><span id='field_generated_id25681_18916007_label_span' class='entlabel'>
<label class='entlabel small' for='street'>Straat</label>
</span>
<span id='field_generated_id25681_18916007_input_td' class='entview'>
	<span class="ac_span">
		<input class="ac_input" type="text" name="street" placeholder='Straat' />
	</span>
	</span></div>
	<script type="text/javascript">
jQuery(document).ready(function(){
	var options = [
							'\'s-Gravesandestraat',					'Bentinckstraat',					'Bilderdijkkade',					'Brouwersgracht',					'Cornelis Trooststraat',					'Curacaostraat',					'De Wittenkade',					'Eikenweg',					'Elzenhagensingel',					'Fagelstraat',					'Gerard Callenburgstraat',					'Gloriantstraat',					'Graafschapstraat',					'Haarlemmermeerstraat',					'Haarlemmerweg',					'Hudsonstraat',					'Jan Evertsenstraat',					'Johan van Soesdijkstraat',					'John Franklinstraat',					'Kinderdijkstraat',					'Koggestraat',					'Koopvaardersplantsoen',					'Kostverlorenstraat',					'Krugerplein',					'Marco Polostraat',					'Mercatorstraat',					'Michelangelostraat',					'Middenweg',					'Nassaukade',					'Nepveustraat',					'Nieuwe Nieuwstraat',					'Nieuwevaartweg',					'Nova Zemblastraat',					'Oleanderstraat',					'Oostzaanstraat',					'Orteliuskade',					'Postjeskade',					'Rozengracht',					'Rozenstraat',					'Sanderijnstraat',					'Spaarndammerstraat',					'Theo Frenkelhof',					'Uiterwaardenstraat',					'Van Hallstraat',					'Van Hogendorpstraat',					'Van Nijenrodeweg',					'Van Spilbergenstraat',					'Van Walbeeckstraat',					'Westlandgracht',					'Wilhelmina Druckerstraat',					'Wilhelminastraat',					'Woestduinstraat',					'Zocherstraat',					'Zwinstraat',			];
	$('#field_generated_id25681_18916007 input').autocomplete(options, {
		mustMatch: true,
		matchContains: false,
		max: 20,
		noRecord: "Geen resultaat"
	});
	});
	</script>

</div>	<input id="generated_id25681_18916020" type="hidden" name="bouwvorm" value="" />

	<input id="generated_id25681_18916021" type="hidden" name="resultsPerPage" value="" />

	<input id="generated_id25681_18916022" type="hidden" name="objecttype" value="" />

	<div class="row additionalsearchcriteria" id="generated_id25681_18916023"><div id='field_numberofroomsfrom' class='editfieldoutertag  editfieldaantalsearch outertagleft left'><span id='field_numberofroomsfrom_label_span' class='entlabel'>
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

</div>	<input id="generated_id25681_18916026" type="hidden" name="transactiestatus" value="" />


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
												<div id="Koop" class=""><form id="generated_id25681_18916031" class="ogZoekform aanbodZoeken koopWoningenZoekformulier" action="/aanbod/woningaanbod/">
	<div class="row koopfields" id="generated_id25681_18916032">	<input id="generated_id25681_18916033" type="hidden" name="inclkoop" value="true" />

	<input id="generated_id25681_18916034" type="hidden" name="inclhuur" value="false" />

	<div id='field_wonen_koop_cities' class='editfieldoutertag  editfieldcombofieldfilter outertagplaats plaats'><span id='field_wonen_koop_cities_label_span' class='entlabel'>
<label class='entlabel small' for='cities'>Plaats</label>
</span>
<span id='field_wonen_koop_cities_input_td' class='entview'>
		<select name="cities">
					<option value="">Plaats</option>
							<option value="AMSTERDAM" selected data-province="Noord-Holland" >
				Amsterdam			</option>
					<option value="DEVENTER" data-province="Overijssel" >
				Deventer			</option>
					<option value="DIEMEN" data-province="Noord-Holland" >
				Diemen			</option>
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

	<div id='field_generated_id25681_18916036' class='editfieldoutertag  editfieldfilteredautocomplete outertagstraat straat'><span id='field_generated_id25681_18916036_label_span' class='entlabel'>
<label class='entlabel small' for='street'>Straat</label>
</span>
<span id='field_generated_id25681_18916036_input_td' class='entview'>
	<span class="ac_span">
		<input class="ac_input" type="text" name="street" placeholder='Straat' />
	</span>
	</span></div>
	<script type="text/javascript">
jQuery(document).ready(function(){
	var options = [
							'\'s-Gravesandestraat',					'Bentinckstraat',					'Brouwersgracht',					'Cornelis Trooststraat',					'Curacaostraat',					'De Wittenkade',					'Eikenweg',					'Elzenhagensingel',					'Fagelstraat',					'Gerard Callenburgstraat',					'Gloriantstraat',					'Graafschapstraat',					'Haarlemmermeerstraat',					'Haarlemmerweg',					'Hudsonstraat',					'Jan Evertsenstraat',					'Johan van Soesdijkstraat',					'John Franklinstraat',					'Kinderdijkstraat',					'Koggestraat',					'Koopvaardersplantsoen',					'Kostverlorenstraat',					'Krugerplein',					'Marco Polostraat',					'Mercatorstraat',					'Michelangelostraat',					'Middenweg',					'Nassaukade',					'Nepveustraat',					'Nieuwe Nieuwstraat',					'Nieuwevaartweg',					'Nova Zemblastraat',					'Oleanderstraat',					'Oostzaanstraat',					'Orteliuskade',					'Postjeskade',					'Rozengracht',					'Rozenstraat',					'Sanderijnstraat',					'Spaarndammerstraat',					'Theo Frenkelhof',					'Uiterwaardenstraat',					'Van Hallstraat',					'Van Hogendorpstraat',					'Van Nijenrodeweg',					'Van Spilbergenstraat',					'Van Walbeeckstraat',					'Westlandgracht',					'Wilhelmina Druckerstraat',					'Wilhelminastraat',					'Woestduinstraat',					'Zocherstraat',					'Zwinstraat',			];
	$('#field_generated_id25681_18916036 input').autocomplete(options, {
		mustMatch: true,
		matchContains: false,
		max: 20,
		noRecord: "Geen resultaat"
	});
	});
	</script>

<div id='field_pricefrom' class='editfieldoutertag  editfieldpricesearch outertagprijsvanaf left prijsvanaf left'><span id='field_pricefrom_label_span' class='entlabel'>
<label class='entlabel header' for='pricefrom'>Prijsklasse van:</label>
</span>
<span id='field_pricefrom_input_td' class='entview'>
<select name="pricefrom">
			<option value="-1" >Koopprijs vanaf</option>
			<option value="50000" >&euro; 50.000</option>
			<option value="75000" >&euro; 75.000</option>
			<option value="100000" >&euro; 100.000</option>
			<option value="125000" >&euro; 125.000</option>
			<option value="150000" >&euro; 150.000</option>
			<option value="175000" >&euro; 175.000</option>
			<option value="200000" >&euro; 200.000</option>
			<option value="225000" >&euro; 225.000</option>
			<option value="250000" >&euro; 250.000</option>
			<option value="275000" >&euro; 275.000</option>
			<option value="300000" >&euro; 300.000</option>
			<option value="325000" >&euro; 325.000</option>
			<option value="350000" >&euro; 350.000</option>
			<option value="375000" >&euro; 375.000</option>
			<option value="400000" >&euro; 400.000</option>
			<option value="450000" >&euro; 450.000</option>
			<option value="500000" >&euro; 500.000</option>
			<option value="550000" >&euro; 550.000</option>
			<option value="600000" >&euro; 600.000</option>
			<option value="650000" >&euro; 650.000</option>
			<option value="700000" >&euro; 700.000</option>
			<option value="750000" >&euro; 750.000</option>
			<option value="800000" >&euro; 800.000</option>
			<option value="900000" >&euro; 900.000</option>
			<option value="1000000" >&euro; 1.000.000</option>
			<option value="1250000" >&euro; 1.250.000</option>
			<option value="1500000" >&euro; 1.500.000</option>
			<option value="2000000" >&euro; 2.000.000</option>
	</select>
</span></div>

<div id='field_priceto' class='editfieldoutertag  editfieldpricesearch outertagprijstot right prijstot right'><span id='field_priceto_label_span' class='entlabel'>
<label class='entlabel header' for='priceto'>tot:</label>
</span>
<span id='field_priceto_input_td' class='entview'>
<select name="priceto">
			<option value="-1" >Koopprijs tot</option>
			<option value="50000" >&euro; 50.000</option>
			<option value="75000" >&euro; 75.000</option>
			<option value="100000" >&euro; 100.000</option>
			<option value="125000" >&euro; 125.000</option>
			<option value="150000" >&euro; 150.000</option>
			<option value="175000" >&euro; 175.000</option>
			<option value="200000" >&euro; 200.000</option>
			<option value="225000" >&euro; 225.000</option>
			<option value="250000" >&euro; 250.000</option>
			<option value="275000" >&euro; 275.000</option>
			<option value="300000" >&euro; 300.000</option>
			<option value="325000" >&euro; 325.000</option>
			<option value="350000" >&euro; 350.000</option>
			<option value="375000" >&euro; 375.000</option>
			<option value="400000" >&euro; 400.000</option>
			<option value="450000" >&euro; 450.000</option>
			<option value="500000"  selected>&euro; 500.000</option>
			<option value="550000" >&euro; 550.000</option>
			<option value="600000" >&euro; 600.000</op

Prijs
€ 490.000,- k.k.
Wilhelmina Druckerstraat 13 2
1066 AB Amsterdam
Meer info
"""

from bs4 import BeautifulSoup
import re

def extract_pb_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    base_url = "https://www.pbmakelaars.nl"

    for obj in soup.select("div.blok"):
        try:
            text = obj.get_text(separator="|").strip()
            parts = [part.strip() for part in text.split("|") if part.strip()]

            # Address
            address = next((p for p in parts if re.search(r"\d{4}\s?[A-Z]{2}", p)), None)
            street = next((p for p in parts if re.search(r"\d", p) and "straat" in p.lower()), None)
            full_adres = f"{street} in Amsterdam" if street else (f"{address} in Amsterdam" if address else None)

            # Price (fixed parsing)
            price_text = next((p for p in parts if "€" in p), None)
            price = None
            if price_text:
                price_match = re.search(r"€\s?([\d\.,]+)", price_text)
                if price_match:
                    price_str = price_match.group(1).replace(".", "").replace(",", ".")
                    price = float(price_str)

            # Area
            area_match = re.search(r"(\d+)\s*m²", text)
            area = int(area_match.group(1)) if area_match else None

            # Number of rooms
            room_match = re.search(r"(\d+)\s+kamers?", text, re.IGNORECASE)
            num_rooms = int(room_match.group(1)) if room_match else None

            # URL
            link_tag = obj.select_one("a[href]")
            url = link_tag["href"] if link_tag else None
            if url and not url.startswith("http"):
                url = base_url + url

            listings.append({
                "full_adres": full_adres,
                "url": url,
                "city": "Amsterdam",
                "price": price,
                "area": area,
                "num_rooms": num_rooms,
                "available": "Beschikbaar"
            })
        except Exception:
            continue

    return listings
