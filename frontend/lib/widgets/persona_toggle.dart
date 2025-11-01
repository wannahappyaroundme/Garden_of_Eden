/// Persona Toggle Widget (Adam/Eve Switcher)
library;

import 'package:flutter/material.dart';
import '../utils/constants.dart';

class PersonaToggle extends StatelessWidget {
  final PersonaType currentPersona;
  final ValueChanged<PersonaType> onChanged;

  const PersonaToggle({
    super.key,
    required this.currentPersona,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: UIConstants.spacingLG,
        vertical: UIConstants.spacingMD,
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          _PersonaButton(
            persona: PersonaType.adam,
            isSelected: currentPersona == PersonaType.adam,
            onTap: () => onChanged(PersonaType.adam),
          ),
          const SizedBox(width: UIConstants.spacingLG),
          _PersonaButton(
            persona: PersonaType.eve,
            isSelected: currentPersona == PersonaType.eve,
            onTap: () => onChanged(PersonaType.eve),
          ),
        ],
      ),
    );
  }
}

class _PersonaButton extends StatelessWidget {
  final PersonaType persona;
  final bool isSelected;
  final VoidCallback onTap;

  const _PersonaButton({
    required this.persona,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: UIConstants.animQuick,
        curve: Curves.easeInOut,
        padding: const EdgeInsets.symmetric(
          horizontal: UIConstants.spacingLG,
          vertical: UIConstants.spacingSM,
        ),
        decoration: BoxDecoration(
          border: Border(
            bottom: BorderSide(
              color: isSelected
                  ? Color(UIConstants.electricCyan)
                  : Colors.transparent,
              width: 2,
            ),
          ),
        ),
        child: Text(
          persona.displayName,
          style: theme.textTheme.labelSmall?.copyWith(
            fontSize: UIConstants.fontLabel,
            fontWeight: FontWeight.w600,
            letterSpacing: 1.0,
            color: isSelected
                ? Color(UIConstants.offWhite)
                : Color(UIConstants.lightGrey),
          ),
        ),
      ),
    );
  }
}
