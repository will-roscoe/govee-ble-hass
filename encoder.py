from typing import Dict, List, Tuple, Union
from functools import reduce
import logging
logger = logging.getLogger(__name__)



























class Encoder:
    inf = {
        "default":{
            "seg":[12,14], # default, when brightness not set
            "id" :1 
            },
        "brightness":{
            "seg":[5,7],
            "id":2
        }
    }
    _def = {
        "base":[51,5,21,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        "assigns":[
            "id","id","id","action_id",False,False,False,False,False,False,
            False,False,False,False,"null","null","null","null"
            ],
        "mode":"default",
    }
    def __init__(self, flip:Dict[str,bool]={"horizontal":False,"vertical":False}):
        self._base = Encoder._def["base"]
        self._assigns = Encoder._def["assigns"]
        self.mode = Encoder._def["mode"]
        self._segments = [
            [0,0,0,0,0,0],
            [0,0,0,0,0,0]
            ]
        self.segments_changed = False
        self.seg_ints = [None,None]
        self.flip = flip
        

    def _assign(self, index:int, value:int, ctx:Union[str,bool]=True) -> None:
        """Assigns an identifier to a value in the context of an action on the base array, and assigns the value to the base array if the index is not already assigned."""
        if not self._assigns[index]:
            self._base[index] = value
            self._assigns[index] = ctx
        else:
            raise RuntimeError(f"Value at index \033[1m {index} \033[1m already set to {self._base[index]} in the context of {self._assigns[index]} The segments in question are: {self._segments}")
    
    def segments(self, segments:List[List[int]]) -> None:
        """Assigns the input segments to the _segments array, and flags the segments as changed."""
        if len(segments) == 2 and all(len(seg)==6 for seg in segments):
            self._segments = segments
            self.segments_changed = True
        else:
            raise ValueError("Segments must be a list of two lists with 6 elements each.")
    
    def rgb(self, r:int, g:int, b:int) -> None:
        """Assigns the input r,g,b values to the base array with a 'rgb' tag"""
        if all(x in range(0,256) for x in[r,g,b]):
            [self._assign(ind,col,"rgb") for col,ind in zip([r,g,b], [4,5,6])]
            
        else:
            raise ValueError("rgb values must be between 0-255")
            
    
    def temp(self, temp:int) -> None: #TODO: Figure out a basic way to set temperature
        logger.warning("temp method not implemented, more dev needed to decode bytearray.")
    
    
    def brightness(self, percent:int) -> None:
        """Assigns the brightness to the base array with a 'brightness' tag"""
        if percent<=100 and percent>=0:
            self._assign(4,percent,"brightness")
            self.mode = "brightness"
        else:
            raise ValueError("brightness values must be between 0-100")

    def set_single_segment(self, side:int, index:int):
        """returns the correct array for a single segment operation"""
        base = [
            [0,0,0,0,0,0],
            [0,0,0,0,0,0]
            ]
        base[side][index] = 1
        return base




    def segment_ints(self) -> List[int]:
        """takes the predefined arrays in self._segments and encodes the segments to decimal values for the bytearray.
        
        self._segments[0]: left, self._segments[1]: right"""
        s = self._segments
        L,R = [0,1] if not self.flip["horizontal"] else [1,0]
        ids = [5,4,3,2,1,0] if not self.flip["vertical"] else range(0,6)
        lst_b = [
            0,0,0,0,
            s[L][ids[0]],s[L][ids[1]],s[L][ids[2]],s[L][ids[3]]  
            ]
        lst_a = [
            s[L][ids[4]],s[L][ids[5]],s[R][ids[0]],s[R][ids[1]],
            s[R][ids[2]],s[R][ids[3]],s[R][ids[4]],s[R][ids[5]]
            ]
        a = sum(v << i for i, v in enumerate(lst_a[::-1]))
        b = sum(v << i for i, v in enumerate(lst_b[::-1]))
        return a,b

    
    def _return_state(self) -> List[int]:
        """Returns the base array with the current state of the encoder as a list of decimal integers."""
        self._base[3] = self.inf[self.mode]["id"]
        ind = self.inf[self.mode]["seg"]
        if self.segments_changed:
             self.seg_ints = self.segment_ints()
        self._base[ind[0]:ind[1]] = self.seg_ints
        return self._base
    
    def _checksum(self, *args):
        """returns the xor of all the args"""
        return reduce(lambda x, y: x ^ y, args)

    def _pack_state(self, lst:List[int])-> bytearray:
        """Packs the list of integers into a bytearray."""
        bytearr_ = bytearray(lst)
        checksum_ = self._checksum(*bytearr_)
        bytearr_.append(checksum_)
        return bytearr_
    
    def encode(self, revert=True, **kwargs)-> bytearray:
        """Encodes the current state of the encoder into a bytearray. There are several ways to encode the state:
        
        - `rgb`:`Tuple[int]`: Sets the rgb values of the encoder.
        - `brightness`:`int`: Sets the brightness of the encoder.
        - `temp`:`int`: Sets the temperature of the encoder.[Not implemented]
        - `segments`:`List[List[int]]`: Sets the segments of the encoder.
        - `segment`:`Tuple[int,int]`: Sets a single segment of the encoder.
        - `flip`:`Dict[str,bool]`: Flips the encoder horizontally or vertically. Default is False.

        If `revert` is set to True, the encoder will revert to its default state after encoding the state. If `revert` is set to False, the encoder will retain the state after encoding the state. Default is True.
        """
        self.flip = {
            "horizontal":False,
            "vertical":False
            } if kwargs.get("flip") is None else kwargs.get("flip")
        if kwargs.get("rgb") is not None:
            self.rgb(*kwargs.get("rgb"))
        if kwargs.get("brightness") is not None:
            self.brightness(kwargs.get("brightness"))
        if kwargs.get("temp") is not None:
            self.temp(kwargs.get("temp"))
        if kwargs.get("segments") is not None:
            self.segments(kwargs.get("segments"))
        if kwargs.get("segment") is not None:
            self.segments(self.set_single_segment(*kwargs.get("segment")))
        b10array = self._return_state()
        if revert:
            self._base = Encoder._def["base"]
            self._assigns = Encoder._def["assigns"]
            self.mode = Encoder._def["mode"]
        return self._pack_state(b10array)
    