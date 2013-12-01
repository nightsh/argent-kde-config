/*
 *   Copyright (C) 2007 Tobias Koenig <tokoe@kde.org>
 *   Copyright (C) 2009 Matthias Fuchs <mat69@gmx.net>
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

function init()
{
    comic.comicAuthor = "Randall Munroe";
    comic.websiteUrl = "http://xkcd.com/";
    comic.shopUrl = "http://store.xkcd.com/";

    comic.requestPage(comic.websiteUrl, comic.User);
}

function pageRetrieved(id, data)
{
    //find the most recent strip
    if (id == comic.User) {
        var re = new RegExp("Permanent link to this comic: http://xkcd.com/(\\d+)/");
        var match = re.exec(data);
        if ( match != null ) {
            comic.lastIdentifier = match[1];
            comic.websiteUrl += comic.identifier + "/";
            comic.requestPage(comic.websiteUrl, comic.Page);
        } else {
            comic.error();
        }
    }
    if (id == comic.Page) {
        var re = new RegExp("<img src=\"(http://imgs.xkcd.com/comics/[^\"]+)\"");
        var match = re.exec(data);
        if (match != null) {
            comic.requestPage(match[1], comic.Image);
        } else {
            comic.error();
            return;
        }

        //find the tooltip and the strip title of the comic
        re = new RegExp("src=\"http://imgs.xkcd.com/comics/.+\" title=\"([^\"]+)\" alt=\"([^\"]+)\"");
        match = re.exec(data);
        if (match != null) {
            comic.additionalText = match[1];
            comic.title = match[2];
        }
    }
}
