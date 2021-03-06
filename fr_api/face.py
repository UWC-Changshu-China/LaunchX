# Coding: UTF-8

from PIL import Image, ImageDraw
import face_recognition as fr
import numpy
import hashlib
import glob


class Face(object):

    """ class Face is used to store information for a single face in the image

        :attr: box[0]: a list that store the location of the face in the original image
        :attr: ary_image: a face image in numpy array form
        :attr: pil_image: the same face image in PIL form
        :attr: face_landmarks: a dictionary that store the locations of facial features
        :attr: blackbg_img: an image that have all the facial features marked in white on a black background in PIL form
        :attr: identity: a list that generated by face_recognition mdoel to help identify the face.
        :attr: __hash_identity: the hash value of identity given above 
    """

    def __init__(self):

        self.box = [0] * 4
        self.ary_image = []
        self.pil_image = 0
        self.face_landmarks = {}
        self.blackbg_img = 0
        self.identity = []
        self.__hash_identity = -1

class FacesImage(object):

    """ class FacesImage is for the original image from the camera. It has various kinds of methods to help process the image

        :attr: ary_image: original image in numpy array form
        :attr: pil_image: original image in PIL image form
        :attr: faces_list: a list that contains all the face objects that are located in the image
    """

    def __init__ (self, img_location):

        self.ary_image = fr.load_image_file(img_location)
        self.pil_image = Image.fromarray(self.ary_image)
        self.faces_list = []

    def _locate_faces(self):

        """ use face_locations method in fr to locate all the faces in the image

            :return: a list that store the location of the face in the original image
        """

        face_locations = fr.face_locations(self.ary_image)

        return face_locations

    def _padding(self, box, pixel):

        """ add a certain number of pixel around the face

            :param: box: the coordinates of the face
            :param: pixel: the number of pixel you what to add
        """

        box[0] -= pixel
        box[1] -= pixel
        box[2] += pixel
        box[3] += pixel

    def _regularize_locations(self, face_locations):

        """ create a Face object for each face and store the regularized coordinate in them. 
            Then, append the Face object in faces_list attr

            :param: face_locations: a list of locations given by _locate_face function
        """

        for face_location in face_locations:
            tmpbox = [0] * 4
            for i in range(4):
                tmpbox[i] = face_location[i]

            tmpface = Face()

            tmpface.box[0] = tmpbox[3]
            tmpface.box[1] = tmpbox[0]
            tmpface.box[2] = tmpbox[1]
            tmpface.box[3] = tmpbox[2]

            self._padding(tmpface.box, 15)

            self.faces_list.append(tmpface)

    def _crop_faces(self):

        """ use crop function in PIL module to crop the faces in the image and store them seperately in their attr

        """

        face_locations = self._locate_faces()
        self._regularize_locations(face_locations)

        tmp_pil_image = Image.fromarray(self.ary_image)

        for face in self.faces_list:
            face.pil_image = tmp_pil_image.crop(face.box)
            face.ary_image = numpy.array(face.pil_image)
            # print(str(face.box))
            # face.pil_image.show()
          

    def _get_face_landmarks(self):

        for face in self.faces_list:

            try:
                face.face_landmarks = fr.face_landmarks(face.ary_image)[0]
                
            except IndexError:
                print("No feature detected")
                self.faces_list.remove(face)
                continue

            # for facial_feature in face.face_landmarks.keys():
                # print("The {} in this face has the following points: {}".format(facial_feature, face.face_landmarks[facial_feature]))

    def _draw_facial_feature_on_img(self):

        for face in self.faces_list:

            d_image = ImageDraw.Draw(face.pil_image)

            for facial_feature in face.face_landmarks.keys():

                d_image.line(face.face_landmarks[facial_feature], width = 3)

            # Show the picture
            # face.pil_image.show()
        


    def _draw_feature_map(self):

        for face in self.faces_list:

            face.blackbg_img = Image.new("RGB", self.pil_image.size)

            d_black_img = ImageDraw.Draw(face.blackbg_img)

            for facial_feature in face.face_landmarks.keys():

                origin_landmarks = []
                
                for landmark in face.face_landmarks[facial_feature]:

                    tmpmark = [0] * 2
                    tmpmark[0] = face.box[0] + landmark[0]
                    tmpmark[1] = face.box[1] + landmark[1]

                    tmpmark = tuple(tmpmark)

                    origin_landmarks.append(tmpmark)


                d_black_img.line(origin_landmarks, width = 3)

            # Show the picture
            

            # face.blackbg_img.show()

    def _faces_identification(self):

        for face in self.faces_list:

            try:

                face.identity = fr.face_encodings(face.ary_image)[0]
                md5 = hashlib.md5()
                md5.update(str(face.identity).encode('utf-8'))
                face.__hash_identity = md5.hexdigest()
                print(face.__hash_identity)
            
            except IndexError:

                print("face_identification: No face detected")

                # print(face.identity)

    def run(self):

        # crop faces in the image, store them in both array form and pil form
        self._crop_faces()

        # extract and draw facial feature on faces, generate feature maps
        self._get_face_landmarks()
        self._draw_facial_feature_on_img()
        self._draw_feature_map()

        # identify faces, store hash value of face identity
        self._faces_identification()

    def show(self):

        for face in self.faces_list:

            face.blackbg_img.show()

    def save(self, path):

        # for face in self.faces_list:

        self.faces_list[0].blackbg_img.save(path)



if __name__ == '__main__':

    file_names = glob.glob(r'./pic/*.JPG')
    file_names.sort()

    print(file_names)

    for file in file_names:

        save_path = "feature/{}.png".format(file[6:10])
        face_image = FacesImage(file)
        face_image.run()
        face_image.show()

        # face.blackbg_img.save("feature/{}.png".format(self.index))
