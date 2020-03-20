import sys, os
import xbmcgui
import xbmcplugin
import xbmcaddon
from xml.dom import minidom
from urllib import request
from PIL import Image

addon_handle = int(sys.argv[1])

userdata_path = xbmc.translatePath('special://userdata/addon_data')
root = os.path.join(userdata_path, xbmcaddon.Addon().getAddonInfo('id'))

def compose_image(bg_local_path, fg_local_path, output):
	bg = Image.open(bg_local_path)
	fg = Image.open(fg_local_path)
	(bg_h, bg_w) = bg.size
	(fg_h, fg_w) = fg.size
	h = int((bg_h - fg_h) / 2)
	w = int((bg_w - fg_w) / 2)
	bg.paste(fg, (h, w), fg)
	bg.save(output, "PNG", quality = 100, optimize = True, progressive = True)

def populate_list():
	url = 'http://digital.100fm.co.il/ChannelList_Kodi.xml'
	channels_file = root + '/list.xml'

	if not os.path.exists(root):
		os.makedirs(root)

	request.urlretrieve(url, channels_file)
	digital_sheet = minidom.parse(channels_file)
	channels = digital_sheet.firstChild.getElementsByTagName('Channel')
	entries = list()
	default_pic = None
	img_counter = 1

	for channel in channels:
		label = str(channel.getElementsByTagName('name')[-1].firstChild.nodeValue).encode('utf-8')
		bg_path = channel.getElementsByTagName('img')[-1].firstChild.nodeValue
		fg_path = channel.getElementsByTagName('font')[-1].firstChild.nodeValue
		bg_local_path = root + '/' + os.path.basename(bg_path)
		fg_local_path = root + '/' + os.path.basename(fg_path)

		got_pics = False
		try:
			request.urlretrieve(bg_path, bg_local_path)
			request.urlretrieve(fg_path, fg_local_path)
			got_pics = True
		except:
			if not default_pic:
				raise

		if got_pics:
			img_local_path = root + '/channel_id' + str(img_counter) + '.png'
			img_counter += 1
			compose_image(bg_local_path, fg_local_path, img_local_path)
			if not default_pic:
				default_pic = img_local_path
		else:
			img_local_path = default_pic

		#xbmc.log('got: ' + str(label) + ', img: ' + str(bg_path) + ', font: ' + str(fg_path) + 'img_local_path: ' + img_local_path, xbmc.LOGNOTICE)
		try:
			stream = channel.getElementsByTagName('Feed')[-1].firstChild.nodeValue
		except:
			stream = channel.getElementsByTagName('Feed1')[-1].firstChild.nodeValue

		entries.append((label, img_local_path, stream))

	return entries

def load_channels():
	for ent in populate_list():
		(label, img_local_path, stream) = ent
		channel_ent = xbmcgui.ListItem(label = label)
		channel_ent.setArt({'thumb': img_local_path, 'icon': img_local_path, 'fanart': img_local_path})
		channel_ent.setProperty('IsPlayable', 'true')
		xbmcplugin.addDirectoryItem(addon_handle, stream, channel_ent, False)

	xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
	xbmcplugin.endOfDirectory(addon_handle)

if __name__ == '__main__':
	load_channels()
