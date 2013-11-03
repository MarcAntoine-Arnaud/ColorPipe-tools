import os
import sys
#import traceback

import cherrypy
import plot_that_lut

current_dir = os.path.dirname( os.path.abspath( __file__ ) )


class PlotThatLutWeb(object):
	def __init__( self ):
		if not os.path.exists( os.path.join( current_dir, 'uploads' ) ):
			os.mkdir( os.path.join( current_dir, 'uploads' ) )

	@cherrypy.expose
	def index( self ):
		page = open( os.path.join( current_dir, "html", "index.html" ), "r" ).read()
		return page

	@staticmethod
	def __copyUploadedFile( upfile ):
		"""Copy uploaded file on the server and return its path"""
		all_data = ''
		while True:
			data = upfile.file.read( 8192 )
			if not data:
				break
			all_data += data
		# copy uploaded file on the server
		backup_filename = os.path.join( current_dir, 'uploads', upfile.filename )
		saved_file = open( backup_filename, 'wb' )
		saved_file.write( all_data )
		saved_file.close()
		return backup_filename

	@cherrypy.expose
	def upload( self, lutfile, lut_type, count, custom_count, inverse=False, prelutfile=None, postlutfile=None ):
		# copy uploaded files on the server to use it with plot_that_lut
		backup_filename = self.__copyUploadedFile( lutfile )
		backup_pre_filename = None
		backup_post_filename = None

		label = 'Displaying : ' + backup_filename + ' (type : ' + lut_type
		if prelutfile.file:
			backup_pre_filename = self.__copyUploadedFile( prelutfile )
		if postlutfile.file:
			backup_post_filename = self.__copyUploadedFile( postlutfile )
		# init args
		label += ', samples : '
		if count == 'custom':
			label += str( int( custom_count ) )
		else:
			label += str( count )

		label += ', inverted : '
		if inverse:
			label += "Yes"
		else:
			label += "No"
		label += ')'

		if prelutfile.file:
			label += ('<br/>Pre-LUT : ' + backup_pre_filename )
		if postlutfile.file:
			label += ('<br/>Post-LUT : ' + backup_post_filename )

		# call plot_that_lut to export the graph
		try:
			result_path = plot_that_lut.plot_that_lut( backup_filename, lut_type,
											 tmp_count, inverse,
											 backup_pre_filename,
											 backup_post_filename)
			result = '<img src="/' + result_path + '" width=640 height=480 border=0 />'
		except Exception, e:
			error = str( e ).replace( '\n', '<br/>' )
			result = '<h2>Something went wrong ! </h2><br/><font color="#FF0000">' + error + '</font><br>'
			#print traceback.format_exc()

		return label + '<br/>' + result + '<br/><a href=javascript:history.back()>Go back</a>'


config = {
	'/html': {
		'tools.staticdir.on': True,
		'tools.staticdir.dir': os.path.join( current_dir, 'html' )
	},
	'/css': {
		'tools.staticdir.on': True,
		'tools.staticdir.dir': os.path.join( current_dir, 'css' )
	},
	'/img': {
		'tools.staticdir.on':  True,
		'tools.staticdir.dir': os.path.join( current_dir, 'img' )
	},
	'/uploads': {
		'tools.staticdir.on':  True,
		'tools.staticdir.dir': os.path.join( current_dir, 'uploads' )
	},
}

def application( environ, start_response ):
		cherrypy.config.update( {} )
		cherrypy.tree.mount( PlotThatLutWeb(), script_name="/", config=config )
		return cherrypy.tree( environ, start_response )
