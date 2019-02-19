#!/usr/bin/env python3

import usb.core
import usb.util
import wx
from enum import Enum, IntEnum, unique

#
#USB code
#

@unique
class State(IntEnum):
  ENABLED = 1
  DISABLED = 0

@unique
class InputType(Enum):
  # Apogee Duet uses this value for each input type, that's why I choose these values 
  LINE_4DBU = 0
  LINE_10DBV = 1
  MICROPHONE = 2
  INSTRUMENT = 3
  
  def __str__(self):
    string_representations = {
      self.LINE_4DBU: '+4dBu',
      self.LINE_10DBV: '-10dBV',
      self.MICROPHONE: 'Microphone',
      self.INSTRUMENT: 'Instrument'
    }
    return string_representations[self]
    
  @classmethod
  def str_list(cls):
    return [str(t) for t in list(cls)]

class Input(object):
  _level_range = {
    InputType.MICROPHONE: { 
      'max': 75,
      'min': 0
    },
    InputType.INSTRUMENT: {
      'max': 65,
      'min': 0
    }
  }
  
  def __init__(self, device, index):
    self._device = device
    self.index = index
    self.number = index + 1
    self._type = device.get_input_type(self)
    self._level = device.get_input_level(self)
    if self._type == InputType.MICROPHONE:
      self.phantom_power_state = device.get_phantom_power_state(self)
    self.phase_state = device.get_phase_state(self)
    self.softlimit_state = device.get_softlimit_state(self)
    self.group_state = device.get_group_state(self)
    
  @property
  def min_level(self):
    return self._level_range[self._type]['min']
  
  @property
  def max_level(self):
    return self._level_range[self._type]['max']
    
  @property
  def type_(self):
    return self._type    
    
  @type_.setter
  def type_(self, value):
    new_type = InputType(value)
    self._device.set_input_type(self, new_type)
    self._type = new_type

  @property
  def level(self):
    return self._level

  @level.setter
  def level(self, value):
    self._device.set_input_level(self, value)
    self._level = value
    
  def toggle_phantom_power(self):
    new_state = State(not self.phantom_power_state)
    self._device.set_phantom_power_state(self, new_state)
    self.phantom_power_state = new_state
    
  def toggle_phase(self):
    new_state = State(not self.phase_state)
    self._device.set_phase_state(self, new_state)
    self.phase_state = new_state
    
  def toggle_softlimit(self):
    new_state = State(not self.softlimit_state)
    self._device.set_softlimit_state(self, new_state)
    self.softlimit_state = new_state

  def toggle_group(self):
    new_state = State(not self.group_state)
    self._device.set_group_state(new_state)
    self.group_state = new_state

@unique 
class OutputSource(Enum):
  PLAYBACK_1_2 = 0
  PLAYBACK_3_4 = 1
  MIXER = 2

  def __str__(self):
    string_representations = {
      self.PLAYBACK_1_2: '1-2',
      self.PLAYBACK_3_4: '3-4',
      self.MIXER: 'Mixer'
    }
    return string_representations[self]

  @classmethod
  def str_list(cls):
    return [str(t) for t in list(cls)]

@unique
class SpeakerOutputType(Enum):
  # Apogee Duet uses this value for each input type, that's why I choose these values
  LINE_4DBU = 0
  LINE_10DBV = 1

  def __str__(self):
    string_representations = {
      self.LINE_4DBU: '+4dBu',
      self.LINE_10DBV: '-10dBV'
    }
    return string_representations[self]

  @classmethod
  def str_list(cls):
    return [str(t) for t in list(cls)]

@unique
class OutputType(Enum):
  # Apogee Duet uses this value for each input type, that's why I choose these values
  SPEAKERS = 0
  HEADPHONES = 1

  def __str__(self):
    string_representations = {
      self.SPEAKERS: 'Speakers',
      self.HEADPHONES: 'Headphones'
    }
    return string_representations[self]

class Output(object):
  _level_range = {
    'min': -64,
    'max': 0
  }
  min_level = _level_range['min']
  max_level = _level_range['max']
  
  def __init__(self, device, index):
    self._device = device
    self.index = index
    # Hard coded here, maybe in the future could be read from the device but I haven't been able to do it
    # I just used the "self.index" because speakers are already 0 and headphones are 1 from what I observed
    self.type_ = OutputType(self.index) 
    if self.type_ == OutputType.SPEAKERS:
      self._speaker_output_type = device.get_speaker_output_type(self)
    self.mute_state = device.get_mute_state(self)
    self.dim_state = device.get_dim_state(self)
    self.mono_state = device.get_mono_state(self)
    self._level = device.get_output_level(self)
    self._source = device.get_output_source(self)

  def toggle_mute(self):
    new_state = State(not self.mute_state)
    self._device.set_mute_state(self, new_state)
    self.mute_state = new_state

  def toggle_dim(self):
    new_state = State(not self.dim_state)
    self._device.set_dim_state(self, new_state)
    self.dim_state = new_state

  def toggle_mono(self):
    new_state = State(not self.mono_state)
    self._device.set_mono_state(self, new_state)
    self.mono_state = new_state

  @property
  def level(self):
    return self._level

  @level.setter
  def level(self, value):
    self._device.set_output_level(self, value)
    self._level = value

  @property
  def spekaer_output_type(self):
    return self._speaker_output_type    
    
  @spekaer_output_type.setter
  def spekaer_output_type(self, value):
    new_type = SpeakerOutputType(value)
    self._device.set_speaker_output_type(self, new_type)
    self._speaker_output_type = new_type

  @property
  def source(self):
    return self._source    
    
  @source.setter
  def source(self, value):
    new_source = OutputSource(value)
    self._device.set_output_source(self, new_source)
    self._source = new_source


@unique 
class SoftwareReturnSource(Enum):
  PLAYBACK_1_2 = 0
  PLAYBACK_3_4 = 1

  def __str__(self):
    string_representations = {
      self.PLAYBACK_1_2: '1-2',
      self.PLAYBACK_3_4: '3-4',
    }
    return string_representations[self]

  @classmethod
  def str_list(cls):
    return [str(t) for t in list(cls)]

@unique
class ChannelType(Enum):
  INPUT = 0
  SOFTWARE_RETURN = 1
  MASTER = 2
  
  def __str__(self):
    string_representations = {
      self.INPUT: 'Input',
      self.SOFTWARE_RETURN: 'Software Return',
      self.MASTER: 'Master',
    }
    return string_representations[self]
    
class Channel(object):
  _level_range = {
    'min': -48,
    'max': 6,
  }
  _pan_range = {
    'min': -64,
    'max': 64
  }
  min_level = _level_range['min']
  max_level = _level_range['max']
  min_pan = _pan_range['min']
  max_pan = _pan_range['max']

  def __init__(self, device, index, type_):
    self._device = device
    self.index = index
    self.type_ = type_
    if not self.type_ == ChannelType.MASTER:
      self.mute_state = device.get_channel_mute_state(self)
      self.solo_state = device.get_channel_solo_state(self)
      if self.type_ == ChannelType.SOFTWARE_RETURN:
        self._source = device.get_software_return_source(self)

  @property
  def level(self):
    raw_value = self._device.get_channel_level(self)
    return raw_value + self.min_level

  @level.setter
  def level(self, value):
    value_to_device = value - self.min_level
    self._device.set_channel_level(self, value_to_device)

  @property
  def pan(self):
    raw_value = self._device.get_pan_value(self)
    return raw_value - self.max_pan

  @pan.setter
  def pan(self, value):
    value_to_device = value + self.max_pan
    self._device.set_pan_value(self, value_to_device)

  @property
  def source(self):
    return self._source    
    
  @source.setter
  def source(self, value):
    new_source = SoftwareReturnSource(value)
    self._device.set_software_return_source(self, new_source)
    self._source = new_source

  def toggle_mute(self):
    new_state = State(not self.mute_state)
    self._device.set_channel_mute_state(self, new_state)
    self.mute_state = new_state

  def toggle_solo(self):
    new_state = State(not self.solo_state)
    self._device.set_channel_solo_state(self, new_state)
    self.solo_state = new_state


class ApogeeDuet(object):
  idVendor = 0x0c60
  idProduct = 0x0016
  _WRITE = 0x40
  _READ = 0xc0
  _MIXER_CHANNEL_REQUESTS = {
    'SOFTWARE_RETURN_SOURCE': 54,
    'LEVEL': 76,
    'PAN': 77,
    'SOLO': 78,
    'MUTE': 79,
  }
  _OUTPUT_REQUESTS = {
    'LEVEL': 51,
    'MUTE': 53,
    'DIM': 64,
    'SUM_TO_MONO': 70,
    'SOURCE': 83,
    'SPEAKER_OUTPUT_TYPE': 182,
  }
  _INPUT_REQUESTS = {
    'SOFTLIMIT': 17,
    'PHASE': 19,
    'PHANTOM_POWER': 21,
    'TYPE': 22,
    'LEVEL': {
      InputType.MICROPHONE: 52, 
      InputType.INSTRUMENT: 62
    },
    'GROUP': 68,
  }
  
  def __init__(self):
    self._dev = usb.core.find(idVendor=self.idVendor, idProduct=self.idProduct)
    if self._dev is None:
      raise ValueError('Apogee Duet not found')
    # Hardcoded because I haven't implemented how to read inputs and outputs information from interface
    self.inputs = [
      Input(device=self, index=0), # Input 1
      Input(device=self, index=1)  # Input 2
    ]
    self.outputs = [
      Output(device=self, index=0), # Speakers
      Output(device=self, index=1)  # Headphones
    ]
    self.mixer_channels = [
      Channel(device=self, index=0, type_=ChannelType.INPUT),  # Input 1
      Channel(device=self, index=1, type_=ChannelType.INPUT),  # Input 2
      Channel(device=self, index=2, type_=ChannelType.SOFTWARE_RETURN),  # Software Return
      Channel(device=self, index=3, type_=ChannelType.MASTER)   # Mixer Master
    ]
  
  # Every read USB control transfer with the Apogee seems to follow the same format, just one byte returned
  def _get_value_from_device(self, bmRquest=None, wIndex=None):
    assert bmRquest != None
    assert wIndex != None
    bmRequestType = self._READ
    wValue = 0
    bytes_to_read = 1
    ret = self._dev.ctrl_transfer(bmRequestType, bmRquest, wValue, wIndex, bytes_to_read)
    return ret[0]
    
  # The same here for every write USB control transfer
  def _set_value_on_device(self, bmRequest=None, wIndex=None, message=None):
    assert bmRequest != None
    assert wIndex != None
    assert message != None
    bmRequestType = self._WRITE
    wValue = 0
    message = [message]
    assert self._dev.ctrl_transfer(bmRequestType, bmRequest, wValue, wIndex, message)
  
  #
  # Mixer
  #

  def get_channel_mute_state(self, channel=None):
    assert channel != None
    value = self._get_value_from_device(self._MIXER_CHANNEL_REQUESTS['MUTE'], channel.index)
    return State(value)

  def set_channel_mute_state(self, channel=None, state=None):
    self._set_value_on_device(self._MIXER_CHANNEL_REQUESTS['MUTE'], channel.index, state.value)

  def get_channel_solo_state(self, channel=None):
    assert channel != None
    value = self._get_value_from_device(self._MIXER_CHANNEL_REQUESTS['SOLO'], channel.index)
    return State(value)

  def set_channel_solo_state(self, channel=None, state=None):
    self._set_value_on_device(self._MIXER_CHANNEL_REQUESTS['SOLO'], channel.index, state.value)

  def get_channel_level(self, channel=None):
    assert channel != None
    value = self._get_value_from_device(self._MIXER_CHANNEL_REQUESTS['LEVEL'], channel.index)
    return value

  def set_channel_level(self, channel=None, level=None):
    assert channel != None
    assert level != None
    self._set_value_on_device(self._MIXER_CHANNEL_REQUESTS['LEVEL'], channel.index, level)

  def get_pan_value(self, channel=None):
    assert channel != None
    value = self._get_value_from_device(self._MIXER_CHANNEL_REQUESTS['PAN'], channel.index)
    return value

  def set_pan_value(self, channel=None, value=None):
    assert channel != None
    assert value != None
    self._set_value_on_device(self._MIXER_CHANNEL_REQUESTS['PAN'], channel.index, value)

  def get_software_return_source(self, channel=None):
    assert channel != None
    value = self._get_value_from_device(self._MIXER_CHANNEL_REQUESTS['SOFTWARE_RETURN_SOURCE'], channel.index)
    return SoftwareReturnSource(value)

  def set_software_return_source(self, channel=None, source=None):
    self._set_value_on_device(self._MIXER_CHANNEL_REQUESTS['SOFTWARE_RETURN_SOURCE'], channel.index, source.value)

  #
  # Outputs
  #

  def get_output_source(self, output=None):
    assert output != None
    value = self._get_value_from_device(self._OUTPUT_REQUESTS['SOURCE'], output.index)
    return OutputSource(value)

  def set_output_source(self, output=None, source=None):
    self._set_value_on_device(self._OUTPUT_REQUESTS['SOURCE'], output.index, source.value)

  def get_output_level(self, output=None):
    assert output != None
    value = self._get_value_from_device(self._OUTPUT_REQUESTS['LEVEL'], output.index)
    return -value

  def set_output_level(self, output=None, level=None):
    assert output != None
    assert level != None
    self._set_value_on_device(self._OUTPUT_REQUESTS['LEVEL'], output.index, -level)

  def get_mute_state(self, output=None):
    assert output != None
    value = self._get_value_from_device(self._OUTPUT_REQUESTS['MUTE'], output.index)
    return State(value)

  def set_mute_state(self, output=None, state=None):
    self._set_value_on_device(self._OUTPUT_REQUESTS['MUTE'], output.index, state.value)

  def get_dim_state(self, output=None):
    assert output != None
    value = self._get_value_from_device(self._OUTPUT_REQUESTS['DIM'], output.index)
    return State(value)

  def set_dim_state(self, output=None, state=None):
    self._set_value_on_device(self._OUTPUT_REQUESTS['DIM'], output.index, state.value)

  def get_mono_state(self, output=None):
    assert output != None
    value = self._get_value_from_device(self._OUTPUT_REQUESTS['SUM_TO_MONO'], output.index)
    return State(value)

  def set_mono_state(self, output=None, state=None):
    self._set_value_on_device(self._OUTPUT_REQUESTS['SUM_TO_MONO'], output.index, state.value)

  def get_speaker_output_type(self, output=None):
    assert output != None
    # I'm using 0 which is the left channel I guess? 
    # because I'm assuming that the left and right channel have the same type selected. 
    # More details in set_speaker_output_type() 
    value = self._get_value_from_device(self._OUTPUT_REQUESTS['SPEAKER_OUTPUT_TYPE'], 0)
    return SpeakerOutputType(value)

  def set_speaker_output_type(self, output=None, new_type=None):
    assert new_type != None
    assert output != None
    # Here the index values are hardcoded and I don't use output 
    # because I noticed that they change which will be the left and right channel at the same time    
    self._set_value_on_device(self._OUTPUT_REQUESTS['SPEAKER_OUTPUT_TYPE'], 0, new_type.value)
    self._set_value_on_device(self._OUTPUT_REQUESTS['SPEAKER_OUTPUT_TYPE'], 1, new_type.value)

  #
  # Inputs
  #

  def get_input_level(self, input_=None):
    assert input_ != None
    request = self._INPUT_REQUESTS['LEVEL'][input_.type_]
    value = self._get_value_from_device(request, input_.index)
    return value
  
  def set_input_level(self, input_=None, level=None):
    assert level != None
    assert input_ != None
    request = self._INPUT_REQUESTS['LEVEL'][input_.type_]
    self._set_value_on_device(request, input_.index, level)
    
  def get_input_type(self, input_=None):
    assert input_ != None
    value = self._get_value_from_device(self._INPUT_REQUESTS['TYPE'], input_.index)
    return InputType(value)
  
  def set_input_type(self, input_=None, new_type=None):
    assert new_type != None
    assert input_ != None
    # The official app ungroups the inputs before changing the input type
    self.set_group_state(State.DISABLED)
    self._set_value_on_device(self._INPUT_REQUESTS['TYPE'], input_.index, new_type.value)
        
  def get_group_state(self, input_=None):
    assert input_ != None
    value = self._get_value_from_device(self._INPUT_REQUESTS['GROUP'], input_.index)
    return State(value)

  def set_group_state(self, state=None):
    # At least in the case of Apogee Duet, both input are grouped when clicking "group" in any of the two inputs
    for i in self.inputs:
      self._set_value_on_device(self._INPUT_REQUESTS['GROUP'], i.index, state.value)
      i.group_state = state

  def get_softlimit_state(self, input_=None):
    assert input_ != None
    value = self._get_value_from_device(self._INPUT_REQUESTS['SOFTLIMIT'], input_.index)
    return State(value)
    
  def set_softlimit_state(self, input_=None, state=None):
    self._set_value_on_device(self._INPUT_REQUESTS['SOFTLIMIT'], input_.index, state.value)
    
  def get_phase_state(self, input_=None):
    assert input_ != None
    value = self._get_value_from_device(self._INPUT_REQUESTS['PHASE'], input_.index)
    return State(value)
    
  def set_phase_state(self, input_=None, state=None):
    self._set_value_on_device(self._INPUT_REQUESTS['PHASE'], input_.index, state.value)
    
  def get_phantom_power_state(self, input_=None):
    assert input_ != None
    value = self._get_value_from_device(self._INPUT_REQUESTS['PHANTOM_POWER'], input_.index)
    return State(value)
  
  def set_phantom_power_state(self, input_=None, state=None):
    self._set_value_on_device(self._INPUT_REQUESTS['PHANTOM_POWER'], input_.index, state.value)
    
#    
# GUI code
#

apogee_device = None

class InputPanel(wx.Panel):
  def __init__(self, parent, input_):
    wx.Panel.__init__(self, parent)
    
    self._parent = parent
    self._input = input_
    
    csizer = wx.StaticBoxSizer(wx.VERTICAL, self, 'Input {}'.format(self._input.number))
    c = wx.Choice(self, choices=InputType.str_list())
    c.SetSelection(self._input.type_.value)
    c.Bind(wx.EVT_CHOICE, self.on_input_type_changed)
    csizer.Add(c, flag=wx.EXPAND)  
    c = wx.ToggleButton(self, label='Phantom Power')
    if self._input.type_ != InputType.MICROPHONE:
      c.Disable()
    else:
      c.SetValue(self._input.phantom_power_state.value)
    c.Bind(wx.EVT_TOGGLEBUTTON, self.on_phantom_power_toggled)
    csizer.Add(c, flag=wx.EXPAND)
    c = wx.ToggleButton(self, label='Phase')
    c.SetValue(input_.phase_state)
    c.Bind(wx.EVT_TOGGLEBUTTON, self.on_phase_toggled)
    csizer.Add(c, flag=wx.EXPAND)
    c = wx.ToggleButton(self, label='Soft Limit')
    c.SetValue(input_.softlimit_state)
    c.Bind(wx.EVT_TOGGLEBUTTON, self.on_softlimit_toggled)
    csizer.Add(c, flag=wx.EXPAND)
    c = wx.ToggleButton(self, label='Group')
    c.SetValue(input_.group_state)
    c.Bind(wx.EVT_TOGGLEBUTTON, self.on_group_toggled)
    csizer.Add(c, flag=wx.EXPAND)
    c = wx.SpinCtrl(self)
    c.SetRange(input_.min_level, input_.max_level)
    c.SetValue(input_.level)
    c.Bind(wx.EVT_SPINCTRL, self.on_input_level_changed)
    csizer.Add(c, flag=wx.EXPAND)
    
    self.SetSizer(csizer)
    
  def on_phantom_power_toggled(self, event):
    self._input.toggle_phantom_power()
    
  def on_phase_toggled(self, event):
    self._input.toggle_phase()
    
  def on_softlimit_toggled(self, event):
    self._input.toggle_softlimit()

  def on_group_toggled(self, event):
    self._input.toggle_group()
    self._parent.Update()
    
  def on_input_type_changed(self, event):
    self._input.type_ = event.Int

  def on_input_level_changed(self, event):
    self._input.level = event.Int

class InputsPage(wx.Panel):
  def __init__(self, parent):
    wx.Panel.__init__(self, parent)
    
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    
    global apogee_device
    for input_ in apogee_device.inputs:
      input_panel = InputPanel(self, input_)
      sizer.Add(input_panel, flag=wx.EXPAND|wx.ALL, border=10)
    
    self.SetSizer(sizer) 
    
class OutputPanel(wx.Panel):
  def __init__(self, parent, output):
    wx.Panel.__init__(self, parent)

    self._output = output
    
    csizer = wx.StaticBoxSizer(wx.VERTICAL, self, '{}'.format(self._output.type_))
    c = wx.Choice(self, choices=OutputSource.str_list())
    c.SetSelection(self._output.source.value)
    c.Bind(wx.EVT_CHOICE, self.on_source_changed)
    csizer.Add(c, flag=wx.EXPAND)
    c = wx.ToggleButton(self, label='Mute')
    c.Bind(wx.EVT_TOGGLEBUTTON, self.on_mute_toggled)
    c.SetValue(self._output.mute_state)
    csizer.Add(c, flag=wx.EXPAND)
    c = wx.ToggleButton(self, label='Dim')
    c.Bind(wx.EVT_TOGGLEBUTTON, self.on_dim_toggled)
    c.SetValue(self._output.dim_state)
    csizer.Add(c, flag=wx.EXPAND)
    c = wx.ToggleButton(self, label='Mono')
    c.Bind(wx.EVT_TOGGLEBUTTON, self.on_mono_toggled)
    c.SetValue(self._output.mono_state)
    csizer.Add(c, flag=wx.EXPAND)
    c = wx.SpinCtrl(self)
    c.SetRange(self._output.min_level, self._output.max_level)
    c.SetValue(self._output.level)
    c.Bind(wx.EVT_SPINCTRL, self.on_output_level_changed)
    csizer.Add(c, flag=wx.EXPAND)
    if self._output.type_ == OutputType.SPEAKERS:
      c = wx.Choice(self, choices=SpeakerOutputType.str_list())
      c.SetSelection(self._output.spekaer_output_type.value)
      c.Bind(wx.EVT_CHOICE, self.on_speaker_output_type_changed)
      csizer.Add(c, flag=wx.EXPAND)
    
    self.SetSizer(csizer)

  def on_mute_toggled(self, event):
    self._output.toggle_mute()

  def on_dim_toggled(self, event):
    self._output.toggle_dim()

  def on_mono_toggled(self, event):
    self._output.toggle_mono()

  def on_output_level_changed(self, event):
    self._output.level = event.Int

  def on_speaker_output_type_changed(self, event):
    self._output.spekaer_output_type = event.Int
 
  def on_source_changed(self, event):
    self._output.source = event.Int
    
class OutputsPage(wx.Panel):
  def __init__(self, parent):
    wx.Panel.__init__(self, parent)
       
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    
    global apogee_device
    for output in apogee_device.outputs:
      output_panel = OutputPanel(self, output)
      sizer.Add(output_panel, flag=wx.EXPAND|wx.ALL, border=10)
    
    self.SetSizer(sizer)
    
class ChannelPanel(wx.Panel):
  def __init__(self, parent, channel):
    wx.Panel.__init__(self, parent)

    self._channel = channel
    
    csizer = wx.StaticBoxSizer(wx.VERTICAL, self, '{}'.format(self._channel.type_))
    if self._channel.type_ == ChannelType.SOFTWARE_RETURN:
      c = wx.Choice(self, choices=SoftwareReturnSource.str_list())
      c.SetSelection(self._channel.source.value)
      c.Bind(wx.EVT_CHOICE, self.on_source_changed)
      csizer.Add(c, flag=wx.EXPAND)
    if self._channel.type_ == ChannelType.INPUT:
      c = wx.SpinCtrl(self)
      c.SetRange(self._channel.min_pan, self._channel.max_pan)
      c.SetValue(self._channel.pan)
      c.Bind(wx.EVT_SPINCTRL, self.on_pan_value_changed)
      csizer.Add(c, flag=wx.EXPAND)
    if self._channel.type_ != ChannelType.MASTER:
      c = wx.ToggleButton(self, label='Mute')
      c.Bind(wx.EVT_TOGGLEBUTTON, self.on_mute_toggled)
      c.SetValue(self._channel.mute_state)
      csizer.Add(c, flag=wx.EXPAND)
      c = wx.ToggleButton(self, label='Solo')
      c.Bind(wx.EVT_TOGGLEBUTTON, self.on_solo_toggled)
      c.SetValue(self._channel.solo_state)
      csizer.Add(c, flag=wx.EXPAND)
    c = wx.SpinCtrl(self)
    c.SetRange(self._channel.min_level, self._channel.max_level)
    c.SetValue(self._channel.level)
    c.Bind(wx.EVT_SPINCTRL, self.on_channel_level_changed)
    csizer.Add(c, flag=wx.EXPAND)
    
    self.SetSizer(csizer)

  def on_source_changed(self, event):
    self._channel.source = event.Int

  def on_pan_value_changed(self, event):
    self._channel.pan = event.Int

  def on_channel_level_changed(self, event):
    self._channel.level = event.Int

  def on_mute_toggled(self, event):
    self._channel.toggle_mute()

  def on_solo_toggled(self, event):
    self._channel.toggle_solo()

class MixerPage(wx.Panel):
  def __init__(self, parent):
    wx.Panel.__init__(self, parent)

    sizer = wx.BoxSizer(wx.HORIZONTAL)

    global apogee_device
    for channel in apogee_device.mixer_channels:
      channel_panel = ChannelPanel(self, channel)
      sizer.Add(channel_panel, flag=wx.EXPAND|wx.ALL, border=10)

    self.SetSizer(sizer)

class MainFrame(wx.Frame):
  def __init__(self):
    wx.Frame.__init__(self, None, title='Take control')
    
    try:
      global apogee_device
      apogee_device = ApogeeDuet()
      
      panel = wx.Panel(self)
      notebook = wx.Notebook(panel)
      
      inputs_page = InputsPage(notebook)
      outputs_page = OutputsPage(notebook)
      mixer_page = MixerPage(notebook)
      
      notebook.AddPage(inputs_page, 'Inputs')
      notebook.AddPage(outputs_page, 'Outputs')
      notebook.AddPage(mixer_page, 'Mixer')
      
      sizer = wx.BoxSizer()
      sizer.Add(notebook, flag=wx.EXPAND|wx.ALL)
      panel.SetSizer(sizer)
    except ValueError as e:
      st = wx.StaticText(self, label=str(e))
    
    
if __name__ == '__main__':
  app = wx.App()
  MainFrame().Show()
  app.MainLoop()
