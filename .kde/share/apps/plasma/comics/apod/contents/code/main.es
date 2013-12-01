/***************************************************************************
 *   Copyright (C) 2009 Panard <panard@inzenet.org>                        *
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 *   This program is distributed in the hope that it will be useful,       *
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
 *   GNU General Public License for more details.                          *
 *                                                                         *
 *   You should have received a copy of the GNU General Public License     *
 *   along with this program; if not, write to the                         *
 *   Free Software Foundation, Inc.,                                       *
 *   51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA .        *
 ***************************************************************************/

function init() {
    comic.comicAuthor = "NASA";
	comic.firstIdentifier = "1995-06-20";
	comic.websiteUrl = "http://apod.nasa.gov/apod/ap" + comic.identifier.toString("yyMMdd") + ".html";
	comic.requestPage(comic.websiteUrl, comic.Page);
}

function pageRetrieved( id, data ) {
	if ( id == comic.Page ) {
		// find image
		var re = new RegExp("<IMG SRC=\"image/([^\"]+)\"", "i")
		//var re = new RegExp("<IMG SRC=\"image/([^\"]+)\"[^>]*>(.*)$", "i")
		var match = re.exec(data);
		var is_video = false;
		var s = "";
		if (match != null) {
			comic.requestPage("http://apod.nasa.gov/apod/image/"+match[1], comic.Image);
			//s = match[2];
			s = data;
		} else {
			// check if it is a youtube video
			re = new RegExp("src=\"http://www.youtube.com/embed/([^\?\"]+).*");
			match = re.exec(data);
			if (match != null) {
				// display image preview
				comic.requestPage("http://img.youtube.com/vi/"+match[1]+"/0.jpg", comic.Image);
				is_video = true;
				s = data;
			} else {
				// check if it is not a 404
				s = data.toString();
				print("NO MATCH");
				if ( s.search(/Error 404/) ) {
					comic.error();
					return;
				}

				// else it is certainly a video. display logo of NASA.
				comic.requestPage("http://apod.nasa.gov/apod/apod.gif", comic.Image);
				s = s.split("<center>")[2];
			}
		}

		function cleanValue( str ) {
			str = str.replace(/<[^>]+>/g,""); // strip html
			str = str.replace(/[\n\r]/g, " "); // remove newlines
			str = str.replace(/\s\s+/g, " "); // remove doubled white spaces
			str = str.replace(/^\s*\b/, ""); // trim left
			str = str.replace(/\b\s*$/, ""); // trim right
			return str;
		}

		// find title and tooltip
		re = new RegExp("<b>[^<]*</b>");
		match = re.exec(s);
		title = "";
		if ( match != null ) {
			title = match[0];
			title = cleanValue(title);
		}
		if (is_video) {
			title = "(video) " + title;
		}
		comic.title = title;

		parts = s.split("<p>");
		explain = parts[3];
		explain = cleanValue(explain.replace(/Explanation:/, ""));
		comic.additionalText = explain;
	}
}

