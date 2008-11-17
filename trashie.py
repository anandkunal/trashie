# If you have growlnotify in your path - this is going to be zesty

import commands
import objc
from Foundation import *
from AppKit import *
from PyObjCTools import AppHelper

status_images = {
  'empty':'trash-empty.png',
  'full':'trash-full.png'
}

class Trashie(NSObject):
  images = {}
  statusbar = None
  count = 0
  current_count = 0
  poll_seconds = 3

  def update_trashie(self):
    self.current_count = self.count
      
    # Update the count (ignore .DS_Store files - they can be pesky)
    count = commands.getstatusoutput('find ~/.Trash/ -not \( -name "*.DS_Store" \) | wc -l')
    if count[0] == 0:
      # The ~/.Trash/ directory appears in the find - must remove it
      self.count = int(count[1].strip()) - 1
    
    # Update the icon
    if self.count > 0:
      if self.current_count == 0:
        if self.count > 1:
          commands.getstatusoutput('growlnotify --image "trashie.icns" -m "there are %s things in the trash" "trashie"' % (self.count))
        else:
          commands.getstatusoutput('growlnotify --image "trashie.icns" -m "there is 1 thing in the trash" "trashie"')
      self.statusitem.setImage_(self.images['full'])
    else:
      if self.current_count > 0:
        commands.getstatusoutput('growlnotify --image "trashie.icns" -m "yay! the trash is empty!" "trashie"')
      self.statusitem.setImage_(self.images['empty'])

    # Set a tooltip & title
    self.statusitem.setToolTip_('Trashie')
    self.statusitem.setTitle_('(%d)' % (self.count))
      
  def applicationDidFinishLaunching_(self, notification):
    statusbar = NSStatusBar.systemStatusBar()
    
    # Create the statusbar item
    self.statusitem = statusbar.statusItemWithLength_(NSVariableStatusItemLength)
    
    # Load all images
    for i in status_images.keys():
      self.images[i] = NSImage.alloc().initByReferencingFile_(status_images[i])

    # Let it highlight upon clicking
    self.statusitem.setHighlightMode_(1)

    # Build a very simple menu
    self.menu = NSMenu.alloc().init()
    
    # View trash event is bound to view_trash_ method
    # menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('View Trash', 'view:', 't')
    # menuitem.setKeyEquivalentModifierMask_(NSControlKeyMask | NSAlternateKeyMask | NSCommandKeyMask)
    menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('View Trash', 'view:', '')
    self.menu.addItem_(menuitem)
    
    # Empty trash event is bound to empty_trash_ method
    menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Empty Trash', 'empty:', '')
    self.menu.addItem_(menuitem)

    # Separator
    menuitem = NSMenuItem.separatorItem()
    self.menu.addItem_(menuitem)
    
    # Refresh count event is bound to refresh_count_ method
    menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Count Trash Items', 'refresh:', '')
    self.menu.addItem_(menuitem)
    
    # Separator
    menuitem = NSMenuItem.separatorItem()
    self.menu.addItem_(menuitem)
    
    # Default event    
    # menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Quit Trashie', 'terminate:', 'q')
    menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Quit Trashie', 'terminate:', '')
    self.menu.addItem_(menuitem)

    # Assign the menu
    self.statusitem.setMenu_(self.menu)

    # Get the timer going
    self.timer = NSTimer.alloc().initWithFireDate_interval_target_selector_userInfo_repeats_(NSDate.date(), self.poll_seconds, self, 'poll:', None, True)
    NSRunLoop.currentRunLoop().addTimer_forMode_(self.timer, NSDefaultRunLoopMode)
    self.timer.fire()

  def view_(self, notification):
    commands.getstatusoutput('open ~/.Trash/')

  def refresh_(self, notification):
    self.update_trashie()

  def empty_(self, notification):
    commands.getstatusoutput('rm -rf ~/.Trash/*')
    self.update_trashie()

  def poll_(self, notification):
    self.update_trashie()

if __name__ == "__main__":
  app = NSApplication.sharedApplication()
  delegate = Trashie.alloc().init()
  app.setDelegate_(delegate)
  AppHelper.runEventLoop()