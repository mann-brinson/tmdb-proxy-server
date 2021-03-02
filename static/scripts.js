//Test
// console.log(document.styleSheets[0]);

///// SWITCH SCREENS FUNCTIONALITY /////
function selectView(active_page_type, inactive_page_type) {
  var active_page = document.getElementById(active_page_type);
  var inactive_page = document.getElementById(inactive_page_type);
  active_page.style.display = "inline-block";
  inactive_page.style.display = "none";
}

// Works if CORS enabled on flask server
const url1 = "http://localhost:5000/home"; 
var slideIndex1 = 0;
var slideIndex2 = 0;

var req1 = new XMLHttpRequest();
var req2 = new XMLHttpRequest();

req1.onreadystatechange = function() {
  if (req1.readyState == 4 && req1.status == 200) {

    //Construct trending
    var movie_type = "trending";
    var item_type = "item-trending";
    
    divsFromJson(req1, movie_type, item_type); // Working: TEST 3
    showSlides(item_type, slideIndex1); // Working: TEST 4
  }
};
var req2 = new XMLHttpRequest();
req2.onreadystatechange = function() {
  if (req2.readyState == 4 && req2.status == 200) {

    //Construct trending
    var movie_type = "airing";
    var item_type = "item-airing";
    
    divsFromJson(req2, movie_type, item_type); // Working: TEST 3
    showSlides(item_type, slideIndex2); // Working: TEST 4
  }
};
req1.open("GET", url1, true); // asynchronous
req1.send();

req2.open("GET", url1, true); // asynchronous
req2.send();

///// FUNCTIONS /////

// TEST 3: Instead of table, make a list of divs
function divsFromJson(req, movie_type, item_type) {
  // req: xhr request
  // movie_type: key name of movie subset, can be "trending" or "airing"
  var data = req.responseText;
  var data_json = JSON.parse(data);
  // var trending = data_json["trending"];
  var movie_sub = data_json[movie_type];

  // var cont_slides = document.createElement("div");

  // add json data to the table as rows.
  for (var i = 0; i < movie_sub.length; i++) {
    // console.log(movie_sub[i]['name']);

    var slide = document.createElement("div"); //Item header
    // slide.style.cssText ="left-padding:100px;";
    slide.classList.add(item_type);
    
    if (movie_type == "trending") {
      slide.classList.add("container-record");
    } else {
      slide.classList.add("container-record-2");
    }

    //Image
    var img = document.createElement("img");
    // img.style.cssText ="left-padding:100px;";
    const backdrop_path = movie_sub[i]['backdrop_path'];
    img.src = backdrop_path;
    img.style.width = "100%";
    slide.appendChild(img);

    //Name and year
    const name = movie_sub[i]['name']; //Get name
    var year; //Get year
    if (movie_type == "trending") {
      year = movie_sub[i]['release_date'].split("-")[0];
    } else {
      year = movie_sub[i]['first_air_date'].split("-")[0];
    }
    var message = `${name} (${year})`; //Combine name and year
    var text_block = document.createElement("div");
    text_block.className = "text-block";
    var caption = document.createElement("h2");
    caption.innerHTML = message;
    text_block.appendChild(caption);
    slide.appendChild(text_block);

    // Now, add the newly created table with json data, to a container.
    // var divShowData = document.getElementById("trending");
    // console.log({"movie_type": movie_type});
    var divShowData = document.getElementById(movie_type);
    console.log({"divShowData": divShowData});
    
    // divShowData.innerHTML = "";
    divShowData.appendChild(slide);
  }
}

// TEST 4: After rendering json-to-divs, show slides
function showSlides(item_type, slideIndex) {
  var i;
  // var trend_items = document.getElementsByClassName("item-trending");
  // console.log({"item_type": item_type});
  var trend_items = document.getElementsByClassName(item_type);

  // var trend_itemset = document.getElementsById("trending");
  // var trend_items = trend_itemset.getElementsByClassName("movie_item");
  for (i = 0; i < trend_items.length; i++) {
    var test = trend_items[i].innerText;
    // console.log({"Current item" : test})
    trend_items[i].style.display = "none";  
  }
  slideIndex++;

  //Repeat over-and-over
  if (slideIndex > trend_items.length) {slideIndex = 1}

  trend_items[slideIndex-1].style.display = "block";
  // setTimeout(showSlides, 2000); // Change image every 2 secs
  setTimeout(showSlides.bind(null, item_type, slideIndex), 2000);

  // trend_items[0].style.display = "block";
}

//// SEARCH PAGE FUNCTIONALITY ////
document.getElementById("content_type").selectedIndex = -1; //Category field is empty at first

function resetFields() {
  document.getElementById("content_search_form").reset();
  document.getElementById("content_type").selectedIndex = -1;
  document.getElementById("search_results").innerHTML = "";
}


function validateForm() {
  var search_terms = document.getElementById("search_terms").value;
  var content_type = document.getElementById("content_type").value;

  //Check that the input fields are filled up
  if (search_terms == "" || content_type == "") {
    alert("Please fill out valid fields.");
    search_terms.innerHTML = "";
    content_type.innerHTML = "";
    return;
  }

  console.log(search_terms); //Test
  console.log(content_type); //Test

  //REQUEST DRIVER
  const url_base = "http://localhost:5000/search?";
  const query = new URLSearchParams({
      content_type: content_type,
    search_terms: search_terms,
  });

  const url_path = [url_base, query].join('');
  console.log(query.toString());
  console.log(url_path.toString());

  var req3 = new XMLHttpRequest();
  req3.onreadystatechange = function() {
    if (req3.readyState == 4 && req3.status == 200) {
      divsFromJsonSearch(req3); 
    }
  };
  req3.open("GET", url_path, true); // asynchronous
  req3.send();

}

function divsFromJsonSearch(req) {
  // req: xhr request
  var data = req.responseText;
  var data_json = JSON.parse(data);
  var search_result = data_json["search_result"];

  var search_result_container = document.createElement("div");
  search_result_container.classList.add("search_result_content");

  // if the result is nothing
    if (search_result.length == 0) {
      search_result_container.innerHTML = 'No results found';
      search_result_container.style.height = "450px";
      search_result_container.style.color = "white";
      // search_result_container.style.text-align = "center";

      // Return a 'no results found message'
      var divShowData = document.getElementById("search_results");
      divShowData.innerHTML = "";
      divShowData.appendChild(search_result_container);
      return;

    // else, render the found results
    } else {
    // add json data to the table as rows.
    for (var i = 0; i < search_result.length; i++) {

      //Create a record object to hold the extracted features
      var record = document.createElement("div");
      record.classList.add("flex-container-record");
      record.setAttribute("id", "flex-container-record");

      // if (search_result[i]["media_type"] == "movie") {
      console.log('parse movie features here'); //Test

      //// METADATA
      var metadata = document.createElement("div");
      // metadata.style.display = "hidden";
      metadata.setAttribute("id", "metadata");
      metadata.setAttribute("hidden", true);

      var content_id = document.createElement("div");
      content_id.setAttribute("id", "content_id_select");
      content_id.innerHTML = search_result[i]['id'];
      metadata.appendChild(content_id);

      var content_type = document.createElement("div");
      content_type.setAttribute("id", "content_type_select");
      content_type.innerHTML = search_result[i]['media_type'];
      metadata.appendChild(content_type);
      record.appendChild(metadata);

      //// COL 1
      var col1 = document.createElement("div"); //Item header
      col1.classList.add("col_1");
      record.appendChild(col1);

      //Poster path
      var img = document.createElement("img"); 
      const poster_path = search_result[i]['poster_path']
      img.src = poster_path;
      img.classList.add("movie_item_img");
      img.style.width = "185px";
      col1.appendChild(img);

      //// COL 2
      var col2 = document.createElement("div"); //Item header
      col2.classList.add("col_2");
      col2.style.marginLeft = "30px";
      record.appendChild(col2);

      //Title
      var row1 = document.createElement("h2");
      row1.style.width = "500px";
      if (search_result[i]["media_type"] == "movie") {
        row1.innerHTML = search_result[i]['title'];
      } else if (search_result[i]["media_type"] == "tv") {
        row1.innerHTML = search_result[i]['name'];
      }
          col2.appendChild(row1);

      //Year and genres
      var row2 = document.createElement("div");

      if (search_result[i]["media_type"] == "movie") {
        var year = search_result[i]['release_date'].split("-")[0];
      } else if (search_result[i]["media_type"] == "tv") {
        var year = search_result[i]['first_air_date'].split("-")[0];
      }
          // var year = search_result[i]['release_date'].split("-")[0];

      var genres = search_result[i]['genres'].join(', ');
      var message = `${year} | ${genres}`;
      row2.innerHTML = message;
      col2.appendChild(row2);

      //Vote_avg and votes
      var row3 = document.createElement("div");
      var vote_a = document.createElement("span");
      vote_a.style.cssText = "color: #c0100d; padding-right: 10px";
      var vote_avg = search_result[i]['vote_average'];
      var message1 = `&#9733 ${vote_avg}`;
      vote_a.innerHTML = message1;
      row3.appendChild(vote_a);
      

      var vote_c = document.createElement("span");
      var vote_count = search_result[i]['vote_count'];
      var message2 = `${vote_count} votes`;
      vote_c.innerHTML = message2;
      row3.appendChild(vote_c);

      col2.appendChild(row3);

      //Overview
      var row4 = document.createElement("div");
      // row4.style.cssText = "padding-top: 10px; padding-bottom: 10px; overflow: hidden; text-overflow: ellipsis";
      row4.className = "truncate-overflow";
      row4.innerHTML = search_result[i]['overview'];
      col2.appendChild(row4);

      //Show more button
      var row5 = document.createElement("input");
      row5.className = "show-more-button";
      row5.setAttribute('id', 'show_more_button')
      row5.setAttribute('type', 'submit');
      row5.setAttribute('value', 'Show More');

      //// Get Detail Modal ////
      row5.onclick = function() {
        generateDetailsModal(this);
      }
      col2.appendChild(row5);

      //Add the completed record to the search result
      search_result_container.appendChild(record);
    }
    }

    // Now, add the newly created table with json data, to a container.
    var divShowData = document.getElementById("search_results");
    var head = document.createElement("h2");
    head.style.cssText = "color: white;";
    head.innerHTML = "Showing results...";
    head.style.width = "500px";
    divShowData.innerHTML = "";
    divShowData.appendChild(head);
    divShowData.appendChild(search_result_container);
}

function generateDetailsModal(button_element) {
  // Hit the details endpoint, with the derived content_type and content_id
  // button_element: the button element

  // Derive the content_type and content_id query paramters from parent node
  record = button_element.parentElement.parentElement;
  content_type = record.children[0].children[1].innerHTML;
  content_id = record.children[0].children[0].innerHTML;
  
  console.log(content_type);
  console.log(content_id);

  // Construct url
  const url_base = "http://localhost:5000/detail?";
  //Ex: /detail?entity_type=movie&entity_id=155
  const query = new URLSearchParams({
    entity_type: content_type,
    entity_id: content_id,
  });
  const url_path = [url_base, query].join('');

  // Send request to details endpoint
  var req4 = new XMLHttpRequest();
  req4.onreadystatechange = function() {
  if (req4.readyState == 4 && req4.status == 200) {
    divsFromJsonDetail(req4, content_type); 
  }
  };
  req4.open("GET", url_path, true); // asynchronous
  req4.send();
} 

function divsFromJsonDetail(req, content_type) {
  console.log('extract from request here.')

  // Parse the response
  var data = req.responseText;
  var data_json = JSON.parse(data);
  
  var details = data_json["details"]; //Get details
  var credits = data_json["credits"]; //Get credits
  var reviews = data_json["reviews"]; //Get reviews

  // Create an outer shell
  var modal_container = document.createElement("div");
  modal_container.setAttribute("id", "modal_container");
  modal_container.setAttribute("class", "flex-container-detail-2");

  //// ROW 1 : Background
  var row1 = document.createElement("div");
  row1.setAttribute("class", "flex-container-record");

  // Backdrop image
  var img = document.createElement("img"); 
  const backdrop_path = details['backdrop_path']
  img.src = backdrop_path;
  img.style.width = "780px";
  img.style.marginLeft = "auto";
  img.style.marginRight = "auto";
  row1.appendChild(img);

  // Exit tick
  var exit = document.createElement("span");
  exit.setAttribute("class", "close");
  exit.innerHTML = "&times;";
  row1.appendChild(exit);

  modal_container.appendChild(row1);

  //// ROW 2 : Details
  var row2 = document.createElement("div");
  row2.setAttribute("class", "flex-container-detail-2");
  row2.style.paddingLeft = "20px";

  // Title
  var row1_det = document.createElement("h2");
  row1_det.className = "flex-container-record";
  if (content_type == "movie") {
    row1_det.innerHTML = details['title'];
  } else if (content_type == "tv") {
    row1_det.innerHTML = details['name'];
  }
      row2.appendChild(row1_det);

  // Info box
  var info = document.createElement("a");
  info.innerHTML = "&#9432;";
  info.style.cssText = "padding-left: 10px; text-decoration: none; color: #c0100d; font-size: 10; font-size: 14px";
  const tmdb_link = `https://www.themoviedb.org/${content_type}/${details['id']}`;

  info.setAttribute("href", tmdb_link);
  row1_det.appendChild(info);

  // Year | Genres
  var row2_det = document.createElement("h3");
  if (content_type == "movie") {
    var year = details['release_date'].split("-")[0];
  } else if (content_type == "tv") {
    var year = details['first_air_date'].split("-")[0];
  }
      var genres = details['genres'].join(', ');
  var message = `${year} | ${genres}`;
  row2_det.innerHTML = message;

  row2.appendChild(row2_det);

  // Stars, votes
  var row3_det = document.createElement("div");
  var vote_a = document.createElement("span");
  vote_a.style.cssText = "color: #c0100d; padding-right: 10px";
  var vote_avg = details['vote_average'];
  var message1 = `&#9733 ${vote_avg}`;
  vote_a.innerHTML = message1;
  row3_det.appendChild(vote_a);

  var vote_c = document.createElement("span");
  var vote_count = details['vote_count'];
  var message2 = `${vote_count} votes`;
  vote_c.innerHTML = message2;
  row3_det.appendChild(vote_c);

  row2.appendChild(row3_det);

  // Overview
  var row4_det = document.createElement("div");
  row4_det.innerHTML = details['overview'];
  row2.appendChild(row4_det);

  // Languages
  var row5_det = document.createElement("div");
      var languages = details['spoken_languages'].join(', ');
      var message = `Spoken languages: ${languages}`
      row5_det.innerHTML = message;
  row2.appendChild(row5_det);

  modal_container.appendChild(row2);

  //// ROW 3 : Credits

  //Cast header
  var header = document.createElement("h3");
  header.innerHTML = "Cast";
  header.style.cssText = "padding-left: 30px; margin: 0px;";
  modal_container.appendChild(header);

  var row3 = document.createElement("div");
  row3.setAttribute("class", "flex-container-detail-2");

  //Take a list of cast (max 8) and make two separate lists, with max 4 items in each list
  for (var i = 0; i < credits.length; i++) {
    //// Create a record container
    var record = document.createElement("div");
    record.setAttribute("id", "credit_record");
    record.className = "credit_record";

    record.style.backgroundColor = "#f1f1f1";
    record.style.color = "black";
    record.style.textAlign = "center";
    record.style.overflow = "hidden";

    //Profile path
        var img = document.createElement("img"); 
        const profile_path = credits[i]['profile_path']
        img.src = profile_path;
        img.style.width = "185px";
        record.appendChild(img);

        // Name
        var name_div = document.createElement("div");
        name_div.className = "credit_name";
        name_div.style.fontWeight = "bold";
        name_div.style.overflow = "hidden";
        name_div.style.textOverflow = "ellipsis";

        name_div.innerHTML = credits[i]['name'];
        record.appendChild(name_div)

        // AS
        var as_div = document.createElement("div");
        as_div.innerHTML = "AS";
        record.appendChild(as_div)

        // Character
        var char_div = document.createElement("div");
        char_div.className = "credit_name";
        char_div.innerHTML = credits[i]['character'];
        record.appendChild(char_div)

    var row_id = Math.floor(i/4);
    if (i in [0, 4]) {
      var c_row = document.createElement("div");
      c_row.setAttribute("class", "flex-container-record");
      row3.appendChild(c_row);
    }
    row3.children[row_id].appendChild(record);
  }

  modal_container.appendChild(row3);

  //// ROW 4 : Reviews

  //Review header
  var header = document.createElement("h3");
  // header.className = "detail_header";
  header.innerHTML = "Reviews";
  header.style.cssText = "padding-left: 30px; padding-top: 10px; margin: 0px;";
  modal_container.appendChild(header);

  var row4 = document.createElement("div");
  row4.setAttribute("class", "flex-container-detail-2");
  row4.style.cssText = "margin-left: 20px";

  for (var i = 0; i < reviews.length; i++) {
    //review object
    var review = document.createElement("div");

    //username at created_date
    var row1_rev = document.createElement("div");
    var user_a = document.createElement("span");
    user_a.style.cssText = "font-weight: bold; padding-right: 5px;";
    user_a.innerHTML = reviews[i]['username'];
    row1_rev.appendChild(user_a);

    var created_at = document.createElement("span");
    var created = reviews[i]['created_at'];
    var message = `on ${created}`;
    created_at.innerHTML = message;
    row1_rev.appendChild(created_at);

    review.appendChild(row1_rev);

    // Stars, votes
    if (reviews[i]['rating'] != "") {
      var row2_rev = document.createElement("div");
      var rating = reviews[i]['rating'];
      var message = `&#9733 ${rating}`;
      row2_rev.style.color = "#c0100d";
      row2_rev.innerHTML = message;
      review.appendChild(row2_rev);
    }

    //content
    var row3_rev = document.createElement("div");
    row3_rev.classList.add("truncate-overflow");
    row3_rev.style.cssText = "border-bottom: 1px solid black";
    row3_rev.innerHTML = reviews[i]['content'];
    review.appendChild(row3_rev);

    row4.appendChild(review);
  }
  modal_container.appendChild(row4);

  //// Add margin at bottom

    //// Now, add the newly created table with json data, to a container.
    var divShowData = document.getElementById("modal-content");
    divShowData.innerHTML = "";
    divShowData.appendChild(modal_container);

    //// Display the finished modal 

  // Get the modal
  var modal = document.getElementById("myModal");

  // Get the <span> element that closes the modal
  var span = document.getElementsByClassName("close")[0];

  //Fix the background
  var body = document.getElementById("search_results");
  body.style.position = 'fixed';

  // Display the finished modal
  modal.style.display = "block";

  // When the user clicks on <span> (x), close the modal
  span.onclick = function() {
    modal.style.display = "none";
    body.style.position = 'relative';
  }
} 