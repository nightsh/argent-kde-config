/*
 *   Copyright (C) 2011 Emanuel Paz <efspaz@gmail.com>
 *
 *   This program is free software; you can redistribute it and/or modify
 *   it under the terms of the GNU Library General Public License version 2 as
 *   published by the Free Software Foundation
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details
 *
 *   You should have received a copy of the GNU Library General Public
 *   License along with this program; if not, write to the
 *   Free Software Foundation, Inc.,
 *   51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 */

const mainPage = "http://aprogrammerslife.info/";
const wpContent = "wp-content/uploads";
const firstComic = "2011/08/03/are-you-a-programmer/";
const defaultImage = "http://aprogrammerslife.info//wp-content/themes/vdp/images/headers/layoutnovo.png";


function init()
{
    comic.comicAuthor = "@ProgramadorREAL";
    comic.shopUrl = "http://www.vitrinepix.com.br/vidadeprogramador";
    
    comic.websiteUrl = mainPage;
    comic.firstIdentifier = firstComic;
    
    //checks if comic.identifier is empty
    if (comic.identifier != new String()) {
        comic.websiteUrl += comic.identifier;
        comic.requestPage(comic.websiteUrl, comic.Page);	
    } else {
        comic.requestPage(comic.websiteUrl, comic.User);
    }

}

function pageRetrieved( id, data ) {
    //find the most recent comic
    if (id == comic.User) {
        var re = new RegExp("class=\"entry-title\"><a href=\"http://aprogrammerslife.info/([^\"]+)");
        var match = re.exec(data);
        if (match != null) {
            comic.lastIdentifier = match[1];
            comic.identifier = comic.lastIdentifier;
            comic.websiteUrl += comic.identifier;
            comic.requestPage(comic.websiteUrl, comic.Page);
        } else {
            comic.error();
        }
    }
    //get the image and others informations
    if (id == comic.Page) {
        //load the title
        re = new RegExp("class=\"entry-title\"\s*(.*)\>(.*)<");	
	match = re.exec(data);
	if (match != null) {
	  title = decodeURIComponent(escape(match[2]));
	  comic.title = title;
	  comic.additionalText = title;
        }
 
        //load the comic image
        re = new RegExp("<a href=\"http://aprogrammerslife.info/wp-content/uploads([^\"]+)");
        match = re.exec(data);
        if (match != null) {	    
            imageUrl = mainPage + wpContent + match[1];
	    comic.requestPage(imageUrl, comic.Image);
        } else {
	    comic.requestPage(defaultImage, comic.Image);
	    title = "No image";
	    comic.title = title;
	    comic.additionalText = title;
        }
 
        //getting the previous identifier
        re = new RegExp("class=\"nav-previous\"><a href=\"http://aprogrammerslife.info/([^\"]+)");
        match = re.exec(data);
        if ( (match != null) && (comic.identifier != firstComic) ) {
            comic.previousIdentifier = match[1];
        }
 
        //getting the next identifier
        re = new RegExp("class=\"nav-next\"><a href=\"http://aprogrammerslife.info/([^\"]+)");
        match = re.exec(data);
        if (match != null) {
            comic.nextIdentifier = match[1];
        }
    }


}
