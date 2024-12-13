def merge_ass_subtitles(original_file, translated_file, output_file):
    def parse_ass(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        header = []
        dialogue_lines = []

        in_dialogues = False
        for line in lines:
            if line.startswith("[Events]"):
                in_dialogues = True
                header.append(line)
                continue

            if in_dialogues and line.startswith("Dialogue:"):
                dialogue_lines.append(line)
            else:
                header.append(line)

        return header, dialogue_lines

    # Read original and translated subtitle files
    header, original_dialogues = parse_ass(original_file)
    _, translated_dialogues = parse_ass(translated_file)

    if len(original_dialogues) != len(translated_dialogues):
        raise ValueError("The number of subtitles in both files must be the same.")

    # Merge dialogues line by line
    merged_dialogues = []
    for orig, trans in zip(original_dialogues, translated_dialogues):
        orig_parts = orig.split(",", 9)  # Splitting with maxsplit = 9 to separate fields properly
        trans_parts = trans.split(",", 9)

        if len(orig_parts) < 10 or len(trans_parts) < 10:
            raise ValueError("One of the dialogue lines is malformed.")

        orig_text = orig_parts[9].strip()
        trans_text = trans_parts[9].strip()

        # Merge the dialogue texts with a newline separator
        merged_text = f"{orig_text}\\N{trans_text}"

        # Reassemble the dialogue line
        merged_dialogue = ",".join(orig_parts[:9]) + f",{merged_text}\n"
        merged_dialogues.append(merged_dialogue)

    # Write the merged subtitles to the output file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.writelines(header)
        file.writelines(merged_dialogues)

# Example usag