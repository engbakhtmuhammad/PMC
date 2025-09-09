// TextStyles
import 'package:flutter/material.dart';

import 'constants.dart';

splashTitleTextStyle({double? size, Color? color}){
  return TextStyle(
    fontSize: size??20,
    color: color??blackColor,
    fontWeight: FontWeight.bold
  );
}
buttonTextStyle({double? size, Color? color, FontWeight? fontWeight}){
  return TextStyle(
    fontSize: size??16,
    color: color??whiteColor,
    fontWeight: fontWeight??FontWeight.w600
  );
}
titleTextStyle({double? size, Color? color,FontWeight? fontWeight}){
  return  TextStyle(
    fontSize: size??20,
    color: color??blackColor,
    fontWeight: fontWeight??FontWeight.w600
  );
}
subTitleTextStyle({double? size, Color? color,FontWeight? fontWeight}){
  return TextStyle(
    fontSize: size??16,
    color: color??blackLightColor,
    fontWeight: fontWeight??FontWeight.w400
  );
}
descriptionTextStyle({double? size, Color? color,FontWeight? fontWeight}){
  return TextStyle(  
    fontSize: size??14,
    color: color??blackLightColor,
    fontWeight: fontWeight??FontWeight.w400
  );
} 