import 'package:flutter/material.dart';
import '../utils/constants.dart';
import '../utils/style.dart';

class CustomBtn extends StatelessWidget {
  final IconData? icon;
  final String text;
  final VoidCallback? onPressed;
  final double? width;
  final double? height;
  final Color? color;

  const CustomBtn({
    super.key,
    this.icon,
    required this.text,
    this.onPressed,
    this.height,
    this.color,
    this.width,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: width ?? double.infinity,
      height: height ?? 50,
      child: icon == null
          ? FilledButton(
              style: ButtonStyle(
                backgroundColor: MaterialStateProperty.all(color??primaryColor),
                shape: MaterialStateProperty.all<RoundedRectangleBorder>(
                  RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(containerRoundCorner),
                  ),
                ),
              ),
              onPressed: onPressed ?? () {},
              child: Text(text,style: buttonTextStyle(),),
            )
          : FilledButton.icon(
              style: ButtonStyle(
                shape: MaterialStateProperty.all<RoundedRectangleBorder>(
                  RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(containerRoundCorner),
                  ),
                ),
              ),
              onPressed: onPressed ?? () {},
              icon: Icon(icon),
              label: Text(text,style: buttonTextStyle(),),
            ),
    );
  }
} 